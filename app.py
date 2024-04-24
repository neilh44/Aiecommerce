import requests
import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Set up Mistral 7B model and tokenizer
model_name = "EleutherAI/gpt-neo-2.7B"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Replace with your Shopify store URL, API key, and password
shopify_store_url = "https://pehelinternational.myshopify.com"
api_key = "7c95f3efa60af1b7c6fa8e4990a4d716"
password = "040b271d3eba03b994b5a1d18eb72bbc"

# Construct the API URL to fetch product details
url = f"{shopify_store_url}/admin/api/2023-07/products.json"

# Set up authentication headers for Shopify
shopify_headers = {
    "X-Shopify-Access-Token": "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",
    "Content-Type": "application/json"
}

# Function to generate response using Mistral 7B
def generate_response(prompt, max_length=100):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(input_ids, max_length=max_length, num_return_sequences=1)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response

# Function to collect customer details via chat prompt
def collect_customer_details():
    first_name = st.text_input("Customer's First Name:")
    last_name = st.text_input("Customer's Last Name:")
    email = st.text_input("Customer's Email:")
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email
    }

# Function to collect line item details via chat prompt
def collect_line_items():
    variant_id = int(st.number_input("Variant ID:"))  # Ensure it's treated as an integer
    quantity = int(st.number_input("Quantity:"))  # Ensure it's treated as an integer
    
    return [
        {
            "variant_id": variant_id,
            "quantity": quantity
        }
    ]

# Function to collect shipping address details via chat prompt
def collect_shipping_address():
    first_name = st.text_input("Shipping First Name:")
    last_name = st.text_input("Shipping Last Name:")
    address1 = st.text_input("Shipping Address:")
    city = st.text_input("City:")
    province = st.text_input("Province:")
    zip_code = st.text_input("ZIP Code:")
    country = st.text_input("Country:")
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "address1": address1,
        "city": city,
        "province": province,
        "zip": zip_code,
        "country": country
    }

# Function to place an order on Shopify
def place_order():
    st.write("Great! Let's start the order process. Please provide the following information one by one.")
    
    customer_details = collect_customer_details()
    line_items = collect_line_items()
    shipping_address = collect_shipping_address()
    
    order_data = {
        "order": {
            "line_items": line_items,
            "customer": customer_details,
            "shipping_address": shipping_address
        }
    }
    
    response = requests.post(
        f"{shopify_store_url}/admin/api/2023-07/orders.json",
        headers=shopify_headers,
        json=order_data
    )
    
    if response.status_code == 201:
        st.write("Order placed successfully!")
        order_response = response.json()
        # Extract and use order details from order_response as needed
    elif response.status_code == 422:
        st.write("Failed to place the order. Validation Error(s):")
        validation_errors = response.json().get("errors")
        if validation_errors:
            order_errors = validation_errors.get("order")
            if order_errors is not None:
                for error in order_errors:
                    st.write(f"Validation Error: {error}")
    else:
        st.write(f"Failed to place the order. Status code: {response.status_code}")
        st.write("Response Content:")
        st.write(response.text)

# Streamlit App
st.title("Pehel International Product Console")

# User input
user_query = st.text_input("Ask any question about our products")

if user_query:
    if "order" in user_query.lower():
        place_order()
    else:
        # Fetch product data from Shopify
        response = requests.get(url, headers=shopify_headers)
        
        if response.status_code == 200:
            products = response.json().get("products")
            
            if products:
                # Create a list to store product titles and descriptions
                product_info = [(product.get("title"), product.get("body_html")) for product in products]
                
                # Join product titles and descriptions into a single string for the chatbot prompt
                prompt = "\n".join([f"Product: {title}\nDescription: {description}" for title, description in product_info])
                
                # Now you can use the prompt to query the Mistral 7B model
                response = generate_response(prompt)
                
                # Display the generated response
                st.write("Response:")
                st.write(response)
            else:
                st.write("No products found.")
        else:
            st.write("Failed to fetch product data from Shopify. Status code:", response.status_code)
          
