from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from getpass import getpass  # For secure password input

shopping_cart = {}

# Create a SQLite database file
engine = create_engine("sqlite:///pos.db")
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# Define the Product and Customer models
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String)  # Add phone number field
    email = Column(String)  # Add email address field
    transactions = relationship("Transaction", back_populates="customer")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Float)

    product = relationship("Product")
    customer = relationship("Customer", back_populates="transactions")

# Create the tables in the database
Base.metadata.create_all(engine)

# Create a Session
Session = sessionmaker(bind=engine)
session = Session()

# Function to authenticate a user
def authenticate(username, password):
    user = session.query(User).filter_by(username=username, password=password).first()
    return user

# Function to create a new user
def create_user(username, password):
    user = User(username=username, password=password)
    session.add(user)
    session.commit()

# Function to display the product catalog
def display_product_catalog():
    products = session.query(Product).all()
    print("Product Catalog:")
    for product in products:
        print(f"ID: {product.id}, Name: {product.name}, Price: {product.price}, Stock: {product.stock}")

# Function to create a new product
def create_product(name, price, stock):
    product = Product(name=name, price=price, stock=stock)
    session.add(product)
    session.commit()
    print(f"Product '{name}' added successfully!")

# Function to display customer information
def display_customer_info():
    customers = session.query(Customer).all()
    print("Customer Information:")
    for customer in customers:
        print(f"ID: {customer.id}, Name: {customer.name}, Phone: {customer.phone}, Email: {customer.email}")

# Function to create a new customer
def create_customer(name, phone, email):
    customer = Customer(name=name, phone=phone, email=email)
    session.add(customer)
    session.commit()
    print(f"Customer '{name}' added successfully!")

# Function to create a transaction (order)
def create_transaction(customer_name):
    customer = session.query(Customer).filter_by(name=customer_name).first()

    if customer:
        print(f"Shopping Cart for Customer: {customer_name}")
        while True:
            product_name = input("Product Name (or 'done' to finish): ")
            if product_name.lower() == "done":
                break

            quantity = int(input("Quantity: "))

            product = session.query(Product).filter_by(name=product_name).first()

            if product:
                total = product.price * quantity

                if product_name in shopping_cart:
                    shopping_cart[product_name]['quantity'] += quantity
                    shopping_cart[product_name]['total'] += total
                else:
                    shopping_cart[product_name] = {'quantity': quantity, 'total': total}

                print(f"{product_name} (Quantity: {quantity}) added to the shopping cart.")
            else:
                print("Product not found. Please check the name.")

        # Display the summary of the shopping cart
        if shopping_cart:
            print("\nShopping Cart Summary:")
            for product_name, item in shopping_cart.items():
                print(f"Product: {product_name}, Quantity: {item['quantity']}, Total: {item['total']}")
        else:
            print("Shopping cart is empty.")
    else:
        print("Customer not found. Please check the name.")

# Function to view the contents of the shopping cart
def view_shopping_cart():
    if shopping_cart:
        print("\nShopping Cart Contents:")
        for product_name, item in shopping_cart.items():
            print(f"Product: {product_name}, Quantity: {item['quantity']}")

        print("\nTotal Amount in Shopping Cart:")
        total_amount = sum(item['total'] for item in shopping_cart.values())
        print(f"Total: {total_amount}")
    else:
        print("Shopping cart is empty.")

# Function to generate a receipt for the transactions
def generate_receipt(cart):
    customer_name = input("Enter Customer Name for Receipt: ")
    filename = f"receipt_{customer_name}.txt"

    with open(filename, "w") as receipt_file:
        receipt_file.write(f"Receipt for Customer: {customer_name}\n")
        receipt_file.write("-------------------------------\n")

        for product_name, item in cart.items():
            receipt_file.write(f"Product: {product_name}, Quantity: {item['quantity']}, Total: {item['total']}\n")

        total_amount = sum(item['total'] for item in cart.values())
        receipt_file.write(f"Total Amount: {total_amount}\n")

    print(f"Receipt generated and saved as '{filename}'")


# Function to checkout and finalize the transactions
def checkout():
    if shopping_cart:
        customer_name = input("Customer Name: ")
        customer = session.query(Customer).filter_by(name=customer_name).first()

        if customer:
            for product_name, item in shopping_cart.items():
                product = session.query(Product).filter_by(name=product_name).first()

                if product:
                    quantity = item['quantity']
                    total = item['total']
                    
                    transaction = Transaction(
                        product_id=product.id,
                        customer_id=customer.id,
                        quantity=quantity,
                        total=total
                    )

                    session.add(transaction)
                else:
                    print(f"Product '{product_name}' not found.")
            
            session.commit()
            shopping_cart.clear()
            print("Checkout completed. Transactions have been added.")
        else:
            print("Customer not found. Please check the name.")
    else:
        print("Shopping cart is empty. Nothing to checkout.")



# Function to print the main menu
def print_menu():
    print("\nOptions:")
    print("1. Display Product Catalog")
    print("2. Create Product")
    print("3. Display Customer Information")
    print("4. Create Customer")
    print("5. Create Transaction (Order)")
    print("6. View Shopping Cart")
    print("7. Checkout")
    print("8. Logout")

# Main function with user authentication
def main():
    print("Point of Sale System")

    # Check if there are any users in the database
    if session.query(User).count() == 0:
        print("No users found. Please create a user account.")
        username = input("Enter a username: ")
        password = getpass("Enter a password: ")  # Use getpass to securely input passwords
        create_user(username, password)
        print("User account created successfully.")

    authenticated = False
    while not authenticated:
        username = input("Enter username: ")
        password = getpass("Enter password: ")  # Use getpass to securely input passwords

        user = authenticate(username, password)
        if user:
            authenticated = True
            print(f"Welcome, {username}!")

    while authenticated:
        print("\nOptions:")
        print("1. Display Product Catalog")
        print("2. Create Product")
        print("3. Display Customer Information")
        print("4. Create Customer")
        print("5. Create Transaction (Order)")
        print("6. View Shopping Cart")
        print("7. Generate Receipt")  
        print("8. Checkout")  
        print("9. Logout")

        choice = input("Enter your choice: ")

        if choice == "1":
            display_product_catalog()
        elif choice == "2":
            name = input("Product Name: ")
            price = float(input("Price: "))
            stock = int(input("Stock: "))
            create_product(name, price, stock)
        elif choice == "3":
            display_customer_info()
        elif choice == "4":
            name = input("Customer Name: ")
            phone = input("Phone Number: ")
            email = input("Email Address: ")
            create_customer(name, phone, email)
        elif choice == "5":
            customer_name = input("Customer Name: ")
            create_transaction(customer_name)
        elif choice == "6":
            view_shopping_cart()
        elif choice == "7":
            generate_receipt(shopping_cart)
        elif choice == "8":
            checkout()
        elif choice == "9":
            authenticated = False
            print("Logged out.")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
