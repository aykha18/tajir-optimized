import requests
import json
import sys

BASE_URL = "http://localhost:5001/api"

def test_crud():
    print("🚀 Starting CRUD Test for Products and Product Types...")
    
    # 1. Create a Product Type
    print("\n1. Creating Product Type...")
    type_data = {
        "name": "Test Type Auto",
        "description": "Created by automated test"
    }
    try:
        resp = requests.post(f"{BASE_URL}/product-types", json=type_data)
        if resp.status_code == 200:
            type_id = resp.json()['id']
            print(f"✅ Product Type created. ID: {type_id}")
        else:
            print(f"❌ Failed to create Product Type. Status: {resp.status_code}, Resp: {resp.text}")
            return
    except Exception as e:
        print(f"❌ Exception creating Product Type: {e}")
        return

    # 2. Create a Product
    print("\n2. Creating Product...")
    product_data = {
        "type_id": type_id,
        "name": "Test Product Auto",
        "rate": 100.50,
        "description": "Created by automated test",
        "barcode": "TEST-12345"
    }
    product_id = None
    try:
        resp = requests.post(f"{BASE_URL}/products", json=product_data)
        if resp.status_code == 200:
            product_id = resp.json()['id']
            print(f"✅ Product created. ID: {product_id}")
        else:
            print(f"❌ Failed to create Product. Status: {resp.status_code}, Resp: {resp.text}")
    except Exception as e:
        print(f"❌ Exception creating Product: {e}")

    # 3. Update the Product
    if product_id:
        print("\n3. Updating Product...")
        update_data = {
            "type_id": type_id,
            "product_name": "Test Product Auto Updated",
            "rate": 150.00,
            "description": "Updated by automated test",
            "barcode": "TEST-12345-UPD"
        }
        try:
            resp = requests.put(f"{BASE_URL}/products/{product_id}", json=update_data)
            if resp.status_code == 200:
                print(f"✅ Product updated.")
            else:
                print(f"❌ Failed to update Product. Status: {resp.status_code}, Resp: {resp.text}")
        except Exception as e:
            print(f"❌ Exception updating Product: {e}")

    # 4. Try to delete Product Type (Should Fail)
    print("\n4. Attempting to delete Product Type (Should FAIL because it has products)...")
    try:
        resp = requests.delete(f"{BASE_URL}/product-types/{type_id}")
        if resp.status_code == 400:
            print(f"✅ Product Type deletion failed as expected. Resp: {resp.text}")
        elif resp.status_code == 200:
            print(f"❌ Product Type deletion SUCCEEDED but should have FAILED!")
        else:
            print(f"❌ Product Type deletion failed with unexpected status. Status: {resp.status_code}, Resp: {resp.text}")
    except Exception as e:
        print(f"❌ Exception deleting Product Type: {e}")

    # 5. Delete the Product
    if product_id:
        print("\n5. Deleting Product...")
        try:
            resp = requests.delete(f"{BASE_URL}/products/{product_id}")
            if resp.status_code == 200:
                print(f"✅ Product deleted.")
            else:
                print(f"❌ Failed to delete Product. Status: {resp.status_code}, Resp: {resp.text}")
        except Exception as e:
            print(f"❌ Exception deleting Product: {e}")

    # 6. Delete the Product Type (Should Succeed now)
    print("\n6. Attempting to delete Product Type (Should SUCCEED now)...")
    try:
        resp = requests.delete(f"{BASE_URL}/product-types/{type_id}")
        if resp.status_code == 200:
            print(f"✅ Product Type deleted.")
        else:
            print(f"❌ Failed to delete Product Type. Status: {resp.status_code}, Resp: {resp.text}")
    except Exception as e:
        print(f"❌ Exception deleting Product Type: {e}")

if __name__ == "__main__":
    test_crud()
