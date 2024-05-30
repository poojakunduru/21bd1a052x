from fastapi import FastAPI, HTTPException, APIRouter
from typing import List, Optional
import requests
import uuid

app = FastAPI()

router = APIRouter()

BASE_API_ENDPOINT = "http://20.244.56.144/test/companies/AMZ/categories"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzE3MDc3NTY3LCJpYXQiOjE3MTcwNzcyNjcsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6ImU2OTdmMGU3LTNjMDktNDM3ZC04MmNlLTJhNDMwYzQ2ZGE5ZCIsInN1YiI6InBvb2pha3VuZHVydWtwckBnbWFpbC5jb20ifSwiY29tcGFueU5hbWUiOiJnb01hcnQiLCJjbGllbnRJRCI6ImU2OTdmMGU3LTNjMDktNDM3ZC04MmNlLTJhNDMwYzQ2ZGE5ZCIsImNsaWVudFNlY3JldCI6ImVpeHlLc2xqckhTUWNmcVEiLCJvd25lck5hbWUiOiJQb29qYSBrdW5kdXJ1Iiwib3duZXJFbWFpbCI6InBvb2pha3VuZHVydWtwckBnbWFpbC5jb20iLCJyb2xsTm8iOiIyMUJEMUEwNTJYIn0.C7PPPkQ2phNH9UCS2h5B2_ioW81pRbrhVLrBoiJQGsw"

def fetch_products_from_company(category: str, top: int, min_price: int, max_price: int) -> List[dict]:
    endpoint = f"{BASE_API_ENDPOINT}/{category}/products"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    params = {
        "top": top,
        "minPrice": min_price,
        "maxPrice": max_price
    }
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("products", [])
    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching products")

@router.get("/categories/{category_name}/products")
def get_top_products(
    category_name: str, 
    n: int = 10, 
    min_price: int = 1, 
    max_price: int = 10000, 
    page: int = 1,
    sort_by: Optional[str] = None, 
    order: Optional[str] = "asc"
):
    if n > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 products per page allowed.")

    all_products = fetch_products_from_company(category_name, n, min_price, max_price)

    if sort_by:
        reverse = order == "desc"
        all_products.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    
    start = (page - 1) * n
    end = start + n
    paginated_products = all_products[start:end]
    for product in paginated_products:
        product["unique_id"] = str(uuid.uuid4())

    return {"products": paginated_products, "total": len(all_products)}

@router.get("/categories/{category_name}/products/{product_id}")
def get_product_details(category_name: str, product_id: str):
    products = fetch_products_from_company(category_name, 10, 1, 10000)
    for product in products:
        if product.get("unique_id") == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

app.include_router(router)
