# Parking entrance permission

## Installation

### OCR

A Python wrapper for using the ocr.space API.

- Install the ocrspace package to your environement. If you use pip, run the following command:
```bash
pip install ocrspace
```

- [OPTIONAL] The default OCR API key in the code is a free key. You can replace it with yours or get a new one [here](https://ocr.space/ocrapi).
You can replace your key to the 'personal_user_api_key' variable under 'Static vars' at the begining of parking_permission.py or leave it as it is.


### MongoDB

We will use mongoDB in order to store the decisions of whether a vehicle could enter a parking lot or not.

- Install MongoDB. Follow the steps relative to your OS [here](https://docs.mongodb.com/manual/installation/).

- Install the pymongo package to your environement. If you use pip, run the following command:
```bash
python -m pip install pymongo
```

## Usage
Input: The script gets an image of a license plate and decides if the vehicle is allowed to enter.
Finally it logs the event to the database.

```bash
python3 parking_permission.py <path to image> [-v]
```
It will add an event to the log. You can add verbosity with the -v flag.

For more information run: 
```bash
python3 parking_permission.py --help
```

To print the database you can for example call ParkingLogger.get_log() from the main():
```python
if __name__ == "__main__":
    logger = ParkingLogger(db_name=parking_db, collection_name=parking_log_collection)
    logger.get_log()
```

### Examples
You can see examples of negative and positive expected results in the examples/negative/ and examples/positive/ directories respectively.

### Pittfalls
The OCR API sometimes fails to accurately retrieve the car plate, if at all. We added some examples under examples/pittfalls
