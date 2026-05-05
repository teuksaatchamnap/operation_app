# AGENTS.md

## Project Overview

Business intelligence dashboard built with Laravel 12 (PHP 8.2+) backend and Vue 3 + Vuetify 4 + Tailwind CSS 4 frontend.
Uses two database connections: `mysql` (local read-write) and `sims3` (external legacy read-only database).
API docs auto-generated via dedoc/scramble. Authentication via Laravel Sanctum (session-based with Google OAuth).

## Commands

### Running the app
```
composer dev              # Server + queue worker + logs + vite dev (concurrent)
npm run dev               # Vite dev server only
```

### Testing
```
composer test             # Clear config cache + run all tests
php artisan test          # Run all tests
php artisan test --filter=MethodName          # Run a single test method
php artisan test --filter=ClassName           # Run all tests in a class
php artisan test --filter=KpiControllerTest   # Run all tests in a class
php artisan test tests/Feature/KpiControllerTest.php  # Run a specific test file
```

Tests use PHPUnit (not Pest). Test suites: `tests/Feature` and `tests/Unit`.

### Static Analysis & Formatting
```
./vendor/bin/phpstan analyse --memory-limit=512M   # PHPStan level 5 (only app/ directory)
./vendor/bin/pint                                  # Fix code style (PSR-12 / Laravel defaults)
```

### Frontend
```
npm run build              # Production build
npm run dev                # Dev server with HMR
```

### Artisan Commands
```
php artisan compute:all                                          # Compute all data from 2005 to now
php artisan sims3:import-dimensions                              # Import sites/platforms/advisors from sims3
php artisan job:run "App\Jobs\ComputeSalesVolume" --year=2026   # Run a single compute job
php artisan job:run "App\Jobs\ComputeSalesVolume" --month=2026-01
php artisan job:run "App\Jobs\ComputeSalesVolume" --site=M24
```

## Code Style

### Formatting
- **Indentation**: 4 spaces (PHP, JS, CSS). 2 spaces for YAML.
- **Line endings**: LF. Insert final newline. Trim trailing whitespace (except `.md` files).
- **PHP brace style**: Opening brace on same line as declaration (K&R style).
- **PHPDoc**: Use `/** @extends */`, `/** @use */`, and `/** @property */` annotations on models. Use Scramble `@response`/`@queryParam`/`@authenticated` docblocks on controller methods that serve as API endpoints.
- **No `declare(strict_types=1)`** — the codebase does not use strict types.
- **No trailing commas** after the last item in arrays/lists unless the codebase already uses them in that context.

### Imports
Order in PHP files:
1. `namespace` declaration
2. Blank line
3. `use` statements — external packages first (Illuminate, Carbon, Laravel\Sanctum), then app-level (App\Models, App\Http, App\Jobs)
4. Blank line
5. Class declaration

### Naming Conventions
| Element | Convention | Example |
|---|---|---|
| Models | Singular PascalCase | `Advisor`, `FactMonthly` |
| Sims3 models | Namespaced `App\Models\Sims3\*` | `App\Models\Sims3\Sale` |
| Controllers | PascalCase + `Controller` suffix | `KpiController` |
| Jobs | PascalCase | `ComputeSalesVolume`, `BaseComputeJob` |
| Commands | PascalCase | `ComputeAll`, `ImportFromSims3` |
| Command signatures | kebab-case | `compute:all`, `sims3:import-dimensions` |
| Database tables | snake_case | `fact_monthly`, `advisors` |
| Sims3 legacy tables | PascalCase (preserve original) | `Sales`, `Sites`, `Expenses` |
| Methods | camelCase | `getAdvisors()`, `importSites()` |
| Test methods | snake_case with `test_` prefix | `test_can_list_all_kpis` |
| Factories | PascalCase + `Factory` suffix | `UserFactory` |
| Routes (URI) | kebab-case | `/fact-monthly`, `/getAuth` |
| Vue components | PascalCase `.vue` files | `KpiCard.vue`, `DashboardLayout.vue` |
| JS stores | camelCase filenames | `auth.js` |

### Types
- All controller and job methods **must** have return type declarations (`: JsonResponse`, `: void`, `: int`, etc.).
- Method parameters should be typed (`Request $request`, `int $id`, `Collection $siteMap`).
- Use constructor property promotion where appropriate.
- Use the `casts()` method (not `$casts` property) — Laravel 11+ style.

### Error Handling
- Controllers: use `$request->validate([...])` for validation (auto-returns 422). Use `findOrFail()` for model lookups (auto-returns 404). Return explicit `response()->json(['error' => '...'], statusCode)` for custom errors.
- Jobs: use `Log::info(...)` and `Log::warning(...)` — no try/catch in jobs.
- No try/catch in controllers.

## Architecture

### Database Connections
- **`mysql`** (default): Local read-write database. Contains `fact_monthly`, `users`, `advisors`, `platforms`, `sites`, `kpis`.
- **`sims3`**: External legacy read-only database. Same host credentials, different database name (`DB_DATABASE_SIMS3`).

### Sims3 Models (Read-Only)
Located in `app/Models/Sims3/`. These models:
- Set `protected $connection = 'sims3'`
- Use PascalCase `$table` names matching the legacy schema
- Override `performInsert()`, `performUpdate()`, and `performDeleteOnModel()` to prevent writes
- Have `PHPDoc @property` annotations for column types since the legacy schema uses non-standard column names

### Compute Jobs
All compute jobs extend `BaseComputeJob` which provides:
- Batched upsert logic (500 records per batch)
- Deduplication by `site_id + month`
- Key normalization across records
- Uses `FactMonthly::upsert()` with unique columns `['site_id', 'month']`

Subclasses implement `prepareData(Collection $siteMap, Collection $months, array $siteNames): array` returning an associative array keyed by `{siteName}|{YYYY-MM-DD}`.

### API Routes (routes/api.php)
All routes use `auth:sanctum` middleware except `POST /login`.
Controllers return `JsonResponse` exclusively. No Blade rendering from API routes.

### Frontend (Vue 3)
- Entry point: `resources/js/app.js`
- Components: `resources/js/components/`
- Pages (auto-routed): `resources/js/pages/`
- Layouts: `resources/js/layouts/`
- Stores (Pinia): `resources/js/stores/`
- Plugins: `resources/js/plugins/vuetify.js`
- SPA shell: `resources/views/app.blade.php`

## CI
GitHub Actions runs on push: PHP 8.4, MariaDB service, `phpstan analyse`, `php artisan test`, `npm run build`.
