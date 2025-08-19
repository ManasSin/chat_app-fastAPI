// This script runs when the MongoDB container starts for the first time

db = db.getSiblingDB("database");

db.createCollection("messages", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["session_id", "content", "timestamp"],
      properties: {
        session_id: {
          bsonType: "string",
          description: "must be a string and is required",
        },
        content: {
          bsonType: "string",
          description: "must be a string and is required",
        },
        timestamp: {
          bsonType: "date",
          description: "must be a date and is required",
        },
      },
    },
  },
});

db.messages.createIndex({ session_id: 1 });
db.messages.createIndex({ timestamp: -1 });
db.messages.createIndex({ sentiment: 1 });

db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "name"],
      properties: {
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
          description: "must be a valid email and is required",
        },
        name: {
          bsonType: "string",
          description: "must be a string and is required",
        },
      },
    },
  },
});

db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ name: 1 });

print("MongoDB initialization completed successfully");
