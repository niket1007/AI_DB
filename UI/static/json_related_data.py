EXAMPLE_JSON_SCHEMA = """{
  "tables": [
    {
      "name": "users",
      "description": "Table contain user information",
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "primary_key": true,
          "autoincrement": true,
          "nullable": false,
          "description": "User id" 
        },
        {
          "name": "username",
          "type": "VARCHAR",
          "size": 50,
          "unique": true,
          "nullable": false,
          "description": "Username"
        },
        {
          "name": "email",
          "type": "VARCHAR",
          "size": 100,
          "unique": true,
          "nullable": true,
          "description": "User email address"
        },
        {
          "name": "created_at",
          "type": "DATETIME",
          "nullable": false,
          "default": "CURRENT_TIMESTAMP",
          "description": "User record created timestamp"
        },
        {
          "name": "is_active",
          "type": "BOOLEAN",
          "nullable": false,
          "default": "true",
          "description": "Is user active?"
        }
      ]
    },
    {
      "name": "posts",
      "description": "Table contain post data",
      "columns": [
        {
          "name": "id",
          "type": "INTEGER",
          "primary_key": true,
          "autoincrement": true,
          "nullable": false,
          "description": "Post id"
        },
        {
          "name": "title",
          "type": "VARCHAR",
          "size": 200,
          "nullable": false,
          "description": "Post title"
        },
        {
          "name": "content",
          "type": "VARCHAR",
          "size": 10000,
          "description": "Post content"
        },
        {
          "name": "author_id",
          "type": "INTEGER",
          "nullable": true,
          "description": "User id who has written the post"
        }
      ]
    }
  ],
  "relationships": [
    {
      "from_table": "posts",
      "from_column": "author_id",
      "to_table": "users",
      "to_column": "id",
      "on_delete": "SET NULL"
    }
  ],
  "indexes": [
    {
      "name": "idx_post_title",
      "table": "posts",
      "columns": ["title"]
    }
  ]
}"""

VALIDATION_CHECKS_MARKDOWN = """
The backend runs a complete validation of your schema *before*
attempting to create it.

**Table & Column Checks:**
- All table names must be unique.
- Every table must have at least one primary key.
- All column names within a table must be unique.
- `VARCHAR` or `CHAR` types **must** have a positive `size`.
- `INTEGER`, `FLOAT`, etc. **must not** have a `size`.
- `autoincrement: true` requires `type: "INTEGER"` and `primary_key: true`.
- A table cannot have multiple `autoincrement` columns.
- An `autoincrement` column cannot be part of a composite (multi-column) primary key.
- `primary_key: true` columns cannot be `nullable: true`.
- `unique: false` is not allowed on a primary key.
- `default: "CURRENT_TIMESTAMP"` is only allowed for `DATETIME` type.
- `default` for `BOOLEAN` must be `"true"` or `"false"`.

**Relationship (Foreign Key) Checks:**
- `from_table`, `from_column`, `to_table`, and `to_column` must all exist.
- The target column (e.g., `users.id`) **must** be either a `PRIMARY KEY` or have `unique: true`.
- If `on_delete: "SET NULL"`, the `from_column` (e.g., `posts.author_id`) **must** be `nullable: true`.

**Index Checks:**
- All index names must be unique.
- The `table` specified in an index must exist.
- The `columns` list for an index cannot be empty.
- All columns listed in an index must exist on that table.
- Duplicate columns are not allowed within a single index.

**Description and Example Checks:**
- Table and column description is required for chat feature.
- Example are optional but if provided it increases query generation accuracy.
"""
