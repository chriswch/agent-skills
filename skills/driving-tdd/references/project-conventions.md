# Project Test Conventions

## Test Placement

| Test Type | Directory | File Pattern |
|-----------|-----------|--------------|
| Unit: use case (admin) | `spec/use_cases/admin_context/` | `spec/use_cases/admin_context/{domain}/{use_case}_spec.rb` |
| Unit: use case (shop) | `spec/use_cases/shop_context/` | `spec/use_cases/shop_context/{domain}/{use_case}_spec.rb` |
| Unit: service | `spec/services/` | `spec/services/{service}_spec.rb` or `spec/services/{domain}/{service}_spec.rb` |
| Integration (admin) | `spec/integration/admin/` | `spec/integration/admin/{feature}/` |
| Integration (shop) | `spec/integration/shop/` | `spec/integration/shop/{feature}/` |

Spec file paths mirror the source class hierarchy. When placing a new test, find the closest existing spec in the same domain and follow its structure.

## Key Patterns

- Unit tests: `require 'spec_helper'`
- Integration tests: `require 'swagger_helper'`
- Use case specs use `subject { described_class.new(...).execute(...) }`
- Shared contexts: `spec/support/shared_contexts/`
