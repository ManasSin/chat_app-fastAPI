// Create indexes for messages collection
// Run with: mongo <connection-string> init-scripts/02-create-indexes-mongo.js

try {
  db = db.getSiblingDB("database");
} catch (e) {
  // running in different shell
}

print("Creating indexes on messages collection...");

// Unique index on message_id
db.messages.createIndex({ message_id: 1 }, { unique: true, background: true });

// Index on session_id for fast retrieval
db.messages.createIndex({ session_id: 1 }, { background: true });

// Index on sender_id for user based queries
db.messages.createIndex({ sender_id: 1 }, { background: true });

// Compound index for session + timestamp for sorting
db.messages.createIndex(
  { session_id: 1, created_at: -1 },
  { background: true }
);

print("Indexes created");
