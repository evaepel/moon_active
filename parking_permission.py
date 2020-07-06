import ocrspace
import time
import pymongo
import argparse
import sys

# Static vars
personal_user_api_key = '5d62617d4888957'
parking_db = "parking"  # The main database to collect data on the parking
parking_log_collection = "parking_log"  # The collection to log parking lot entrance events
public_transport_last_digits = ['25', '26']
prohibited_last_digits = ['85', '86', '87', '88', '89', '00']
prohibited_car_plate_lens = [7, 8]
car_plate_digit_sum_prohibited_divisor = 7


def connect_to_db(db_name: str) -> pymongo.database.Database:
    """
    This function create a local client to connect to the given database.
    If the given database doesn't exist, a new one is created the database.

    :param: db: The name of databse to access/create.
    :return: the given Database as pymongo Database instance.
    """
    local_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db_cars_license = local_client[db_name]
    return db_cars_license


def get_collection(db_name: str, collection_name: str) -> pymongo.collection.Collection:
    """
    This function accesses the given Database and retrieve the given mongo collection (equivalent to table in SQL).
    If the Database/collection name don't exist, new ones are created.
    Assumption: Mongo is already installed on the machine and exist in the path environment variable.

    :param: db_name: the Database name to retrieve/create
    :param: collection_name: the Collection name to retrieve/create
    :return: The given collection from the given Database as a pymongo Collection instance.
    """
    db = connect_to_db(db_name)
    collection = db[collection_name]
    return collection


class ParkingLogger:
    def __init__(self, db_name: str, collection_name: str):
        self.log = get_collection(db_name, collection_name)

    def info(self, car_plate: str, was_allowed: bool, reason=None, verbose=False):
        """
        This function logs a parking entrance event to its database.

        :param car_plate: the plate of the vehicle that tried to enter the parking lot.
        :param was_allowed: Boolean value describing if the vehicle was allowed to enter the parking lot.
        :param reason: the reason why the vehicle may not enter the parking lot if access was refused.
        :param verbose: print verbosity if true
        """
        if was_allowed:
            self.log.insert_one({"plate": car_plate,
                                 "allowed": "Yes",
                                 "time": time.localtime()})
            if verbose:
                print("Access granted")
        else:
            assert reason is not None, f"Tried to log an access refusal event and no reason was given"
            self.log.insert_one({"plate": car_plate,
                                 "allowed": "No",
                                 "reason": reason,
                                 "time": time.localtime()})
            if verbose:
                print(f"Access denied, {reason}")

    def get_log(self):
        for doc in self.log.find():
            print(doc)


def is_public_transport(car_plate: str) -> bool:
    """
    This function checks if the given car_plate is a public transportation vehicle.
    Public transportation vehicles cannot enter the parking lot (their license
    plates always end with 25 or 26).

    :param car_plate: a string containing the plate of the vehicle
    :return: True if the car_plate is a public transportation vehicle.
    """
    return car_plate[-2:] in public_transport_last_digits


def is_military_or_law(car_plate: str) -> bool:
    """
    This function checks if the given car_plate is a military or law enforcement vehicle.
    Military and law enforcement vehicles are prohibited (these can be
    identified by an inclusion of an English alphabet letter within the plate
    number)

    :param car_plate: a string containing the plate of the vehicle
    :return: True if the car_plate is a military or law enforcement vehicle.
    """
    return any(c.isalpha() for c in car_plate)


def get_plate_digits(car_plate: str) -> list:
    """
    This function parses the car_plate and return only the digits in the order they appear.

    :param car_plate: a string containing the plate of the vehicle
    :return: a list containing only the digits of the car plate
    """
    digits = []
    for elem in car_plate:
        if elem.isdigit():
            digits.append(int(elem))

    return digits


def prohibited_last_two_digits(car_plate: str) -> bool:
    """
    This function checks if the car_plate has 7 digit numbers which their last two digits are 85/86/87/88/89/00

    :param car_plate: a string containing the plate of the vehicle
    :return: True if the car_plate has 7 digit numbers which their last two digits are 85/86/87/88/89/00.
    """
    digits = get_plate_digits(car_plate)
    last_two_digits = str(digits[-2]) + str(digits[-1])
    return len(digits) == 7 and last_two_digits in prohibited_last_digits  # only 7 digit numbers


def is_operated_by_gas(car_plate: str) -> bool:
    """
    This function checks if the given car_plate contains 7 or 8 numbers which their digits sum can be divided by 7.

    :param car_plate: a string containing the plate of the vehicle
    :return: True if the car_plate contains 7 or 8 numbers which their digits sum can be divided by 7.
    """
    digits = get_plate_digits(car_plate)
    return len(digits) in prohibited_car_plate_lens and sum(digits) % car_plate_digit_sum_prohibited_divisor == 0


def issue_permission(parking_logger: ParkingLogger, car_plate: str, verbose=False):
    if is_public_transport(car_plate):  # rule a
        parking_logger.info(car_plate, False, reason="Public transportation vehicle", verbose=verbose)
        return

    if is_military_or_law(car_plate):  # rule b
        parking_logger.info(car_plate, False, reason="Military and law enforcement vehicle", verbose=verbose)
        return

    if prohibited_last_two_digits(car_plate):  # rule c
        parking_logger.info(car_plate, False, reason="7 digits number and last two digits are 85/86/87/88/89/00", verbose=verbose)
        return

    if is_operated_by_gas(car_plate):  # rule d
        parking_logger.info(car_plate, False, reason="Operated by gas", verbose=verbose)
        return

    parking_logger.info(car_plate, True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Issue parking entrance permission.')
    parser.add_argument('pictures', metavar='<picture path>', type=str, nargs='+',
                        help='Picture containing the car plate')
    parser.add_argument('-v', dest='verbose', action='store_const',
                        const=True, default=False,
                        help='add verbosity')
    args = parser.parse_args()

    logger = ParkingLogger(db_name=parking_db, collection_name=parking_log_collection)
    image_to_text_api = ocrspace.API(api_key=personal_user_api_key)

    for pic in args.pictures:
        car_plate = image_to_text_api.ocr_file(pic)
        if car_plate:
            issue_permission(logger, car_plate, verbose=args.verbose)
        else:
            logger.info(car_plate, False, reason="unable to extract the car plate", verbose=args.verbose)
