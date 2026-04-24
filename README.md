# Installation

- Must be installed on the same database server as sims3.
- Sims3 database name must be set in .env DB_DATABASE_SIMS3

```
composer install
php artisan migrate:fresh --seed
php artisan sims3:import-dimensions
```

# Data model

This BI database implements a **star schema** (also known as star model), which is the industry standard for data warehouse design.

## Why Star Schema?

The star schema is the optimal choice for business intelligence and analytical workloads because:

- **Simplified Queries**: All dimension tables connect directly to the fact table, making JOIN operations straightforward and performant
- **Historisation** : As advisor and facts are directly linked we can see in the data the history oif changes
- **Fast Aggregations**: Fact tables contain only measurements and foreign keys, optimized for rapid aggregation of large datasets
- **Intuitive Structure**: Business users can easily understand the model without deep technical knowledge
- **Scalability**: Handles millions or billions of fact records efficiently while keeping dimension tables relatively small
- **Standard**: You can plug this database as it is with PowerBI or Tableau or any BI tool, it will immediately work

## Architecture

The star schema consists of a central **fact_monthly** table surrounded by **dimension tables** (sites, advisors, platforms):

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400">
  <!-- Central Fact Table -->
  <rect x="220" y="170" width="160" height="60" fill="#4A90E2" stroke="#2E5C8A" stroke-width="2" rx="5"/>
  <text x="300" y="190" text-anchor="middle" fill="white" font-size="14" font-weight="bold">fact_monthly</text>
  <text x="300" y="210" text-anchor="middle" fill="white" font-size="10">Monthly KPIs & Metrics</text>

  <!-- Sites Dimension -->
  <rect x="20" y="40" width="120" height="50" fill="#50C878" stroke="#2E8B57" stroke-width="2" rx="5"/>
  <text x="80" y="62" text-anchor="middle" fill="white" font-size="12" font-weight="bold">sites</text>
  <text x="80" y="78" text-anchor="middle" fill="white" font-size="9">id, name</text>
  <line x1="140" y1="65" x2="220" y2="180" stroke="#666" stroke-width="2"/>
  <circle cx="220" cy="180" r="3" fill="#666"/>

  <!-- Advisors Dimension -->
  <rect x="240" y="20" width="120" height="50" fill="#50C878" stroke="#2E8B57" stroke-width="2" rx="5"/>
  <text x="300" y="42" text-anchor="middle" fill="white" font-size="12" font-weight="bold">advisors</text>
  <text x="300" y="58" text-anchor="middle" fill="white" font-size="9">id, name</text>
  <line x1="300" y1="70" x2="300" y2="170" stroke="#666" stroke-width="2"/>
  <circle cx="300" cy="170" r="3" fill="#666"/>

  <!-- Platforms Dimension -->
  <rect x="460" y="40" width="120" height="50" fill="#50C878" stroke="#2E8B57" stroke-width="2" rx="5"/>
  <text x="520" y="62" text-anchor="middle" fill="white" font-size="12" font-weight="bold">platforms</text>
  <text x="520" y="78" text-anchor="middle" fill="white" font-size="9">id, name</text>
  <line x1="460" y1="65" x2="380" y2="180" stroke="#666" stroke-width="2"/>
  <circle cx="380" cy="180" r="3" fill="#666"/>

  <!-- KPIs Reference Table -->
  <rect x="240" y="330" width="120" height="50" fill="#FFA500" stroke="#CC8400" stroke-width="2" rx="5"/>
  <text x="300" y="352" text-anchor="middle" fill="white" font-size="12" font-weight="bold">kpis</text>
  <text x="300" y="368" text-anchor="middle" fill="white" font-size="9">name, col_name, unit</text>
  <line x1="300" y1="330" x2="300" y2="230" stroke="#666" stroke-width="2" stroke-dasharray="5,5"/>
  <circle cx="300" cy="230" r="3" fill="#666"/>

  <!-- Legend -->
  <rect x="20" y="340" width="200" height="50" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="3"/>
  <rect x="30" y="350" width="15" height="10" fill="#4A90E2"/>
  <text x="50" y="358" font-size="9" fill="#333">= Fact Table</text>
  <rect x="30" y="365" width="15" height="10" fill="#50C878"/>
  <text x="50" y="373" font-size="9" fill="#333">= Dimension Tables</text>
  <rect x="110" y="350" width="15" height="10" fill="#FFA500"/>
  <text x="130" y="358" font-size="9" fill="#333">= Reference</text>
</svg>
```

## Tables

### Fact Table

**`fact_monthly`** - Monthly aggregated metrics per site. One column per KPI.

| Column         | Type        | Description                              |
| -------------- | ----------- | ---------------------------------------- |
| id             | integer     | Surrogate primary key                    |
| site_id        | foreign key | → sites.id                               |
| platform_id    | foreign key | → platforms.id                           |
| advisor_id     | foreign key | → advisors.id                            |
| month          | date        | Reporting month                          |
| tier           | string      | Site classification tier                 |
| sales_volume   | integer     | Sales volume (excl. WiS)                 |
| days_open      | integer     | Operating days count                     |
| expenses       | integer     | Total expenses                           |
| revenue        | integer     | Total revenue                            |
| workers        | integer     | Number of workers                        |
| consumers      | integer     | Consumer count                           |
| who_compliance | boolean     | WHO compliance status                    |
| profitable     | boolean     | Profitability flag (P&L + Salary >= 200) |

### Dimension Tables

**`sites`**
**`advisors`**
**`platforms`**

### Reference Table

**`kpis`** - KPI definitions and metadata:
