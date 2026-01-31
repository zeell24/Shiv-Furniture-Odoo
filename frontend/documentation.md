# Shiv Furniture API

## Authentication
- `POST /auth/login`: Accepts `role` (Admin/Contact).

## Transactions
- `GET /invoices`: Returns invoice data.
- [cite_start]`PATCH /invoices/:id`: Updates status to 'Paid' or 'Partially Paid'[cite: 55, 58].

## Rule Engine Logic
- [cite_start]Rules are processed on-client in this hackathon version but should move to server-side for production to maintain master data integrity[cite: 10, 45].