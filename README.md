# Parking entrance permission

## Installation

### OCR

A Python wrapper for using the ocr.space API.

- Get an OCR API key. Follow the steps at [here](https://ocr.space/ocrapi) to get a new key.
You should get an email with your new key.

- Copy your key to the 'personal_user_api_key' variable under 'Static vars' at the begining of the parking_permission.py

- Install the ocrspace package to your environement. If you use pip, run the following command:
```bash
pip install ocrspace
```

### MongoDB

MongoDB stores data in documents (equivalent to rows in a table).
A collection in MongoDB is a container of documents (equivalent to a SQL table). A database is a container of collections.
We will use mongoDB in order to store the decisions of whether a vehicle could enter a parking lot or not.

- Install MongoDB. Follow the steps relative to your OS [here](https://docs.mongodb.com/manual/installation/).

- Install the pymongo package to your environement. If you use pip, run the following command:
```bash
python -m pip install pymongo
```

## Usage
input: The scripts gets an image of a license plate, decides if the vehicle is allowed to enter according to its plate.
Finally it logs the event to the database.

```bash
python3 parking_permission.py <path to your image> [-v]
```

For more information run: 
```bash
python3 parking_permission.py --help
```

To print the database you can add to the main() a call to ParkingLogger.get_log():
```python
if __name__ == "__main__":
    logger = ParkingLogger(db_name=parking_db, collection_name=parking_log_collection)
    logger.get_log()
```

You can see examples of negative and positive expected results in the examples/negative/ and examples/positive/ respectively.

### Pittfalls
The OCR API sometimes fails to accurately retrieve the car plate, if at all. We added some examples under examples/pittfalls
