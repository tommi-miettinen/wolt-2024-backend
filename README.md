# Wolt Summer 2024 Backend Internship assignment

### FastAPI python backend for delivery fee calculations.

### Installation

```
python -m venv venv
```

```
.\venv\Scripts\activate
```

```
pip install -r requirements.txt
```

### Running locally

```
uvicorn main:app --reload
```

### Live demo

#### Send a post request to

https://wolt-backend-2024.azurewebsites.net/deliveryfee

```json
{
  "cart_value": 500,
  "delivery_distance": 1,
  "number_of_items": 4,
  "time": "2024-02-02T15:10:00Z"
}
```

#### Also has a get endpoint for ease of seeing it in action without using tools like postman

https://wolt-backend-2024.azurewebsites.net/deliveryfee?cart_value=500&delivery_distance=1&number_of_items=4&time=2024-02-02T15:10:00Z
