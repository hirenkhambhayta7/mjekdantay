# MJ Masala — Step-by-step project guide (learn to build your own)

This document explains how the MJ Django e-commerce project is structured so you can learn to build something similar. **Save as PDF:** in Cursor/VS Code use **File → Print** and choose **Microsoft Print to PDF**, or open this file in Word/Google Docs and use **Save as PDF**.

---

## 1. What this project is

This is a **Django e-commerce site** for a spice shop: product catalog, shopping cart (guest or logged-in), checkout, **Razorpay** payments, order history, customer profiles and addresses, plus two admin experiences:

- **Django Admin** at `/admin/` (built-in, model-centric).
- **Custom store admin** at `/store-admin/` (dashboard, orders, products, categories, customers) using custom templates and `@staff_member_required`.

**Main stack:** Django 4.x, SQLite for local dev (PostgreSQL optional in `settings.py`), Pillow (images), **django-allauth** (installed alongside custom login/register), **Razorpay** SDK, session-based cart for guests.

---

## 2. Repository map

| Area | Role |
|------|------|
| `mj_masala_project/` | Project config: `settings.py`, root `urls.py`, WSGI. |
| `products/` | Catalog models, storefront views, custom store admin views/forms/urls. |
| `orders/` | Cart, cart items, orders, order lines, payments; checkout and Razorpay. |
| `accounts/` | Register, login, logout, profile, addresses, my orders. |
| `templates/` | HTML: `base.html`, `home.html`, `products/`, `orders/`, `accounts/`, `store_admin/`. |
| `static/` | CSS, JS, images. |
| `media/` | Uploaded images (served in `DEBUG`). |
| `manage.py` | Django CLI. |

---

## 3. How a request flows

1. Browser hits a path in `mj_masala_project/urls.py`.
2. That **includes** app URLs (`products`, `orders`, `accounts`) or store-admin URLs.
3. A **view function** runs (e.g. `products.views.shop`).
4. The view reads/writes **models** and builds a **context** dict.
5. A **template** renders HTML. **Context processors** add global data (categories, cart count).

---

## 4. Configuration (`mj_masala_project/settings.py`)

- **INSTALLED_APPS:** Django built-ins + `allauth` + `products`, `orders`, `accounts`.
- **TEMPLATES:** Folder `templates/`, plus `products.context_processors.categories_processor` and `orders.context_processors.cart_count`.
- **DATABASES:** SQLite → `db.sqlite3` by default.
- **MEDIA_*** / **STATIC_***:** uploads vs static assets.
- **AUTHENTICATION_BACKENDS:** default `User` + allauth.
- **ACCOUNT_***:** email-oriented allauth settings; custom login still resolves user by email.
- **RAZORPAY_KEY_ID / RAZORPAY_SECRET:** from environment (`.env`).
- **LOGIN_URL:** `/accounts/login/` for `@login_required`.

---

## 5. URL wiring

Root patterns (see `mj_masala_project/urls.py`):

- `/admin/` → Django admin.
- `/store-admin/` → `products.admin_urls` (staff dashboard).
- `''` + `products.urls` → home, shop, category, product detail.
- `''` + `orders.urls` → cart, checkout, payment.
- `/accounts/` → local auth + profile URLs and `allauth.urls`.

---

## 6. Data models

### 6.1 Catalog (`products/models.py`)

- **Category:** name, slug, description, optional image.
- **Product:** category FK, slug, description, base price, image, `is_active`, `is_featured`.
- **ProductVariant:** weight label, price, stock per product.

*Idea:* one Product, many Variants — one description, multiple pack sizes/prices.

### 6.2 Cart (`orders/models.py`)

- **Cart:** `user` **or** `session_key` (guest).
- **CartItem:** `unique_together` on `(cart, product_variant)`.

Computed: `subtotal`, `delivery_charge` (free over ₹499, else ₹60), `grand_total`.

### 6.3 Orders and payment

- **Order:** address fields copied onto the row (historical snapshot), totals, `status`, `payment_status`, `razorpay_order_id`.
- **OrderItem:** snapshot `product_name`, `variant_label`, `price_at_purchase` so catalog changes do not rewrite history.
- **Payment:** one-to-one with `Order`; Razorpay ids and status.

### 6.4 Accounts (`accounts/models.py`)

- **UserProfile:** one-to-one with `User` (phone, picture); created by signals.
- **Address:** many per user for checkout.

---

## 7. Storefront (`products/views.py`)

| View | Purpose |
|------|---------|
| `home` | Featured products and categories. |
| `shop` | List, search, category/price filters, sort (`q`, `category`, `min_price`, `max_price`, `sort`). |
| `category_products` | Products in one category. |
| `product_detail` | Detail + variants + related products. |

Uses `select_related`, `prefetch_related`, `Q` for search, `Min('variants__price')` for price filters.

---

## 8. Cart and checkout (`orders/views.py`)

### 8.1 `_get_or_create_cart`

- Authenticated → cart by user.
- Guest → cart by `session_key`.

### 8.2 `merge_cart_on_login`

Guest session cart merges into the user cart after register/login (see `accounts/views.py`).

### 8.3 Endpoints

- `add_to_cart`, `update_cart_item`, `remove_cart_item` — POST; JSON when `X-Requested-With: XMLHttpRequest`.

### 8.4 Checkout

1. `checkout` (`@login_required`) — addresses + Razorpay key in context.
2. `create_order` — creates `Order` and `OrderItem` rows, then Razorpay order; returns JSON for the checkout UI.
3. `payment_success` — verifies Razorpay signature, marks paid, decrements stock with `F()`, clears cart, sends email.
4. If Razorpay errors, code may use a **dev-style fallback** (treat as paid). Review before production.

---

## 9. Accounts (`accounts/views.py`, `accounts/forms.py`)

- **Register:** extends `UserCreationForm`; **username set to email** in `save()`; phone on profile.
- **Login:** email on form → lookup `User` by email → `authenticate(username=..., password=...)`.
- **Profile, addresses, orders:** `@login_required` and `user=request.user` scoping.

---

## 10. Store admin (`products/admin_views.py`)

- `@staff_member_required` → `is_staff=True`.
- URLs in `products/admin_urls.py`, mounted at `/store-admin/`.

Unlike Django admin: custom templates and your own workflows.

---

## 11. Context processors

- **`products.context_processors.categories_processor`:** `all_categories` for navigation.
- **`orders.context_processors.cart_count`:** `cart_item_count` for header (user or session cart).

---

## 12. Rebuild checklist (your own project)

1. Create Django project and apps: `products`, `orders`, `accounts`.
2. Configure `settings.py`: apps, templates, static/media, auth.
3. Define models: categories → products → variants → cart → orders.
4. `makemigrations` / `migrate`.
5. Register models in `admin.py` if useful.
6. Wire URLs with `app_name` for reverse lookups.
7. Storefront views and templates.
8. Cart (session + user), merge on login.
9. Checkout with address snapshot on `Order`.
10. Payment provider: create payment order → client checkout → **server-side verify** → update DB.
11. Staff dashboard: separate URLconf + `@staff_member_required`.
12. Production: env secrets, PostgreSQL, HTTPS, email backend.

---

## 13. Practice exercises

1. Draw an ER diagram from the `models.py` files.
2. Trace one `add_to_cart` request: URL → view → DB → response.
3. Explain why `OrderItem` stores `price_at_purchase`.
4. Add a field end-to-end (e.g. `Order.tracking_number`): model, migration, admin, store-admin, customer template.

---

## 14. Suggested Django learning order

1. Models, migrations, ORM  
2. URLs and views  
3. Templates and forms  
4. Authentication and sessions  
5. Static and media files  
6. Deployment (hosts, database, HTTPS)

---

*Generated for the MJ Masala project. Paths are relative to the repository root.*
