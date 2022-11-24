from config.db_connection import db


# Generating Custom Account id
def generate_custom_id(type, id):
    if id == "new":
        next_gen = db["next_generation"]
        next_gen_data = next_gen.find_one({"type": type})
        if next_gen_data is None:
            next_insert_data = {
                "type": type,
                "sequence_value": 2,
            }
            next_gen.insert_one(next_insert_data)
            id = type + "-" + "1"
        else:

            next_gen.find_one_and_update({"type": type}, {"$inc": {"sequence_value": 1}})
            id = type + "-" + str(next_gen_data["sequence_value"])

        return id
