"""Add addresses table and user.address_id

Revision ID: b535cd4fe926
Revises: b3c9a4d6e7f1
Create Date: 2025-12-22 22:23:05.761247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b535cd4fe926'
down_revision: Union[str, None] = 'b3c9a4d6e7f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        'addresses',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('street', sa.String(255), nullable=False),
        sa.Column('line2', sa.String(255)),
        sa.Column('postal_code', sa.String(32), nullable=False),
        sa.Column('city', sa.String(128), nullable=False),
        sa.Column('country', sa.String(128), nullable=False, server_default="France"),
    )
    op.add_column('users', sa.Column('address_id', sa.String(64), sa.ForeignKey('addresses.id')))
    # Migration des données existantes : créer une adresse pour chaque user
    conn = op.get_bind()
    users = conn.execute(sa.text("SELECT id, address FROM users")).fetchall()
    for u in users:
        if u.address:
            # découpe grossière : rue = première ligne, CP+ville = seconde
            parts = [p.strip() for p in u.address.replace("\\r","").replace("\\n","\n").split("\n") if p.strip()]
            street = parts[0] if parts else ""
            postal_city = parts[1] if len(parts) > 1 else ""
            postal, city = (postal_city.split(" ", 1) + [""])[:2]
            country = parts[2] if len(parts) > 2 else "France"
            conn.execute(sa.text("""
                INSERT INTO addresses (id, street, line2, postal_code, city, country)
                VALUES (:id, :street, :line2, :postal, :city, :country)
            """), {"id": u.id, "street": street, "line2": "", "postal": postal, "city": city, "country": country})
            conn.execute(sa.text("UPDATE users SET address_id=:aid WHERE id=:uid"), {"aid": u.id, "uid": u.id})
    # Optionnel : si tu veux ensuite supprimer l’ancienne colonne address, ajoute op.drop_column('users', 'address')

def downgrade():
    op.drop_column('users', 'address_id')
    op.drop_table('addresses')
