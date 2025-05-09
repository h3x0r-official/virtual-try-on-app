import click
from app import app, db, ClothingItem # Import your Flask app, db instance, and models
from init_db import init_db

# Create a Click command group
@click.group()
def cli():
    """Management commands for the Virtual Try-On backend."""
    pass

@cli.command("create-tables")
def create_tables_command():
    """Creates all database tables based on defined models."""
    with app.app_context(): # Operations need to be within app context
        try:
            db.create_all()
            click.echo("Database tables created successfully.")
        except Exception as e:
            click.echo(f"Error creating tables: {e}", err=True)

@cli.command("drop-tables")
@click.option('--confirm', is_flag=True, help="Confirm dropping all tables. THIS IS DESTRUCTIVE.")
def drop_tables_command(confirm):
    """Drops all database tables. USE WITH EXTREME CAUTION."""
    if not confirm:
        click.echo("Operation aborted. Use --confirm to proceed with dropping tables.", err=True)
        return

    with app.app_context():
        try:
            db.drop_all()
            click.echo("All database tables dropped successfully.")
        except Exception as e:
            click.echo(f"Error dropping tables: {e}", err=True)

@cli.command("add-item")
@click.option('--name', prompt="Item Name", help="Name of the clothing item.")
@click.option('--price', prompt="Price", type=float, help="Price of the item.")
@click.option('--image-url', prompt="Image URL (optional)", default="", help="URL of the item's image.")
@click.option('--brand', prompt="Brand (optional)", default="", help="Brand of the item.")
def add_item_command(name, price, image_url, brand):
    """Adds a new clothing item to the database."""
    if not name or price is None: # Price can be 0.0, so check for None
        click.echo("Error: Name and Price are required.", err=True)
        return

    with app.app_context():
        try:
            new_item = ClothingItem(
                name=name,
                price=price,
                imageUrl=image_url if image_url else None, # Store None if empty string
                brand=brand if brand else None
            )
            db.session.add(new_item)
            db.session.commit()
            click.echo(f"Item '{name}' added successfully with ID: {new_item.id}.")
        except Exception as e:
            db.session.rollback()
            click.echo(f"Error adding item: {e}", err=True)

@cli.command("list-items")
@click.option('--brand', default=None, help="Filter items by brand.")
def list_items_command(brand):
    """Lists clothing items, optionally filtered by brand."""
    with app.app_context():
        try:
            query = ClothingItem.query
            if brand:
                query = query.filter_by(brand=brand)
            
            items = query.all()
            if not items:
                click.echo(f"No items found{f' for brand {brand}' if brand else ''}.")
                return

            click.echo(f"\n--- Clothing Items {f'(Brand: {brand})' if brand else ''} ---")
            for item in items:
                click.echo(
                    f"ID: {item.id}, Name: {item.name}, Price: {item.price:.2f}, "
                    f"Brand: {item.brand or 'N/A'}, ImageURL: {item.imageUrl or 'N/A'}"
                )
            click.echo("---------------------------\n")
        except Exception as e:
            click.echo(f"Error listing items: {e}", err=True)


@cli.command("delete-item")
@click.option('--item-id', prompt="Item ID to delete", type=int, help="ID of the item to delete.")
@click.option('--confirm', is_flag=True, help="Confirm deletion.")
def delete_item_command(item_id, confirm):
    """Deletes a clothing item by its ID."""
    if not confirm:
        click.echo("Operation aborted. Use --confirm to proceed with deletion.", err=True)
        return
        
    with app.app_context():
        try:
            item = ClothingItem.query.get(item_id)
            if not item:
                click.echo(f"Error: Item with ID {item_id} not found.", err=True)
                return
            
            db.session.delete(item)
            db.session.commit()
            click.echo(f"Item '{item.name}' (ID: {item_id}) deleted successfully.")
        except Exception as e:
            db.session.rollback()
            click.echo(f"Error deleting item: {e}", err=True)

@cli.command("update-item")
@click.option('--item-id', prompt="Item ID to update", type=int, help="ID of the item to update.")
# Add options for each field you want to be updatable.
# Using 'None' as default and then checking allows partial updates.
@click.option('--name', default=None, help="New name for the item.")
@click.option('--price', default=None, type=float, help="New price for the item.")
@click.option('--image-url', default=None, help="New image URL for the item. Use 'clear' to remove.")
@click.option('--brand', default=None, help="New brand for the item. Use 'clear' to remove.")
def update_item_command(item_id, name, price, image_url, brand):
    """Updates an existing clothing item by its ID. Only provided fields are updated."""
    with app.app_context():
        try:
            item = ClothingItem.query.get(item_id)
            if not item:
                click.echo(f"Error: Item with ID {item_id} not found.", err=True)
                return

            updated = False
            if name is not None:
                item.name = name
                updated = True
            if price is not None:
                item.price = price
                updated = True
            if image_url is not None:
                item.imageUrl = None if image_url.lower() == 'clear' else image_url
                updated = True
            if brand is not None:
                item.brand = None if brand.lower() == 'clear' else brand
                updated = True

            if updated:
                db.session.commit()
                click.echo(f"Item ID {item_id} updated successfully.")
            else:
                click.echo("No changes specified for update.")
        except Exception as e:
            db.session.rollback()
            click.echo(f"Error updating item: {e}", err=True)

@cli.command("seed-db")
@click.option('--force', is_flag=True, help="Force reinitialization by dropping and recreating tables.")
def seed_db_command(force):
    """Seeds the database with sample data."""
    with app.app_context():
        if force:
            db.drop_all()
            click.echo("Dropped existing tables.")
        db.create_all()
        click.echo("Created tables.")
        try:
            init_db()
            click.echo("Seeded database with sample data successfully.")
        except Exception as e:
            click.echo(f"Error seeding database: {e}", err=True)

if __name__ == '__main__':
    cli()