# Installation

Must be installed on the same database server as sims3.
Sims3 database name must be set in .env DB_DATABASE_SIMS3

```
composer install
php artisan migrate:fresh --seed
php artisan sims3:import-dimensions
```
