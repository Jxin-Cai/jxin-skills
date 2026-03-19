# CodeReview Rules (Continuously Extensible)

This file is the single source of truth for CodeReview rules for `git-auto-commit-review`.

## Table of Contents

- [Rule format](#rule-format-required-for-new-rules)
- [Core rules](#core-rules) (1–14: general review principles)
- **Risk rules (categorized, MECE):**
  - [Payload & data size](#payload--data-size)
  - [Downstream load & call patterns](#downstream-load--call-patterns)
  - [Transactions & consistency](#transactions--consistency)
  - [Concurrency & threading](#concurrency--threading)
  - [Distributed locks](#distributed-locks)
  - [Idempotency & retries](#idempotency--retries)
  - [RPC timeouts & error handling](#rpc-timeouts--error-handling)
  - [Messaging reliability](#messaging-reliability)
  - [Database access & performance](#database-access--performance)
  - [Cache & search](#cache--search)
  - [Multi-tenancy & context propagation](#multi-tenancy--context-propagation)
  - [API contracts & compatibility](#api-contracts--compatibility)
  - [Data validation & correctness](#data-validation--correctness)
  - [Dependency & environment management](#dependency--environment-management)
  - [Logging & observability](#logging--observability)
  - [Testing discipline](#testing-discipline)

---

## Rule format (required for new rules)

When adding a rule, append it using this template:

1. **Rule**: <short imperative rule>
   - **Why**: <one sentence>
   - **Bad**: <short example>
   - **Good**: <short example>

## Core rules

1. **Review both unstaged and staged diffs**
   - **Why**: The final commit content is what is staged, not what is currently modified.
   - **Bad**: Only review `git diff` and miss staged changes.
   - **Good**: Review `git diff` and `git diff --staged`, and reconcile differences.

2. **Explain the “why” for every suggestion**
   - **Why**: Suggestions without rationale are hard to evaluate and easy to ignore.
   - **Bad**: “Refactor this file.”
   - **Good**: “Extract helper to reduce duplication and centralize validation; reduces bug surface.”

3. **Separate must-fix vs nice-to-have**
   - **Why**: Keeps commits moving while still improving quality.
   - **Bad**: Mixed list with no priority.
   - **Good**: Two sections: “Must-fix before commit” and “Nice-to-have”.

4. **Validate correctness and edge cases**
   - **Why**: Most regressions are missing edge-case handling.
   - **Bad**: Assume inputs are always non-empty / non-null.
   - **Good**: Validate inputs; define behavior for empty, null, invalid, and boundary cases.

5. **Prefer small, reviewable changes**
   - **Why**: Smaller diffs reduce risk and improve review quality.
   - **Bad**: Mix refactor + behavior change + formatting in one commit.
   - **Good**: Separate concerns; keep one commit focused.

6. **No new secrets or sensitive data**
   - **Why**: Leaks are expensive and hard to remediate.
   - **Bad**: Commit API keys, tokens, credentials, or internal URLs accidentally.
   - **Good**: Use env vars, secret manager, redaction, and add patterns to `.gitignore` if needed.

7. **Maintain backward compatibility (when applicable)**
   - **Why**: Breaking changes must be intentional and communicated.
   - **Bad**: Rename public API without deprecation strategy.
   - **Good**: Deprecate, keep compatibility layer, or version API.

8. **Handle errors explicitly**
   - **Why**: Silent failures are debugging nightmares.
   - **Bad**: Catch-and-ignore exceptions; swallow error returns.
   - **Good**: Log/return meaningful errors; propagate with context; add tests.

9. **Logging is purposeful and safe**
   - **Why**: Logs can leak data and add noise.
   - **Bad**: Log whole payloads containing PII/secrets.
   - **Good**: Log identifiers/summary; redact sensitive fields; use levels.

10. **Test impact is addressed**
   - **Why**: Changes without tests increase regression risk.
   - **Bad**: Modify behavior with no tests or manual plan.
   - **Good**: Add/adjust tests or document a manual test plan in the report.

11. **Performance risks are called out**
   - **Why**: Small changes can create big hot paths.
   - **Bad**: Add per-request N+1 queries / repeated JSON parsing.
   - **Good**: Cache, batch, avoid repeated work; mention complexity.

12. **Consistency: naming, style, and patterns**
   - **Why**: Inconsistent code is harder to maintain.
   - **Bad**: Introduce a new pattern without reason.
   - **Good**: Follow existing conventions; justify deviations.

13. **Avoid code smells per "Refactoring" by Martin Fowler**
   - **Why**: Code smells indicate deeper design problems that increase maintenance cost and bug risk.
   - **Bad**: Accept Long Method, Large Class, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession, Long Parameter List, Divergent Change, Shotgun Surgery, Message Chains, Middle Man, or Speculative Generality.
   - **Good**: Refactor proactively: extract methods/classes, replace primitives with value objects, remove duplication, encapsulate collections, break god classes, and eliminate unnecessary indirection.

14. **Three pillars of production-ready code: gradual rollout, observability, emergency response**
   - **Why**: Production changes—especially significant business logic modifications—must be controllable to ensure problems can be detected quickly and rolled back safely.
   - **When to apply**: New features, major refactors, changes affecting critical paths, or any modification touching multiple components or business flows.
   - **Bad**:
     - No gradual rollout: Features released to 100% traffic without feature flags; issues require full code rollback.
     - No observability: Missing logs, metrics, or alerts on affected paths; issues cannot be diagnosed quickly.
     - No emergency response: No kill switch, no fallback logic, no fast rollback strategy.
   - **Good**:
     - Gradual rollout: Use feature flags, canary deployments, or A/B experiments to release incrementally; support rollout by tenant, region, or percentage.
     - Observability: Add telemetry logs, business metrics, and anomaly alerts on modified paths; enable rapid detection through dashboards and alerting.
     - Emergency response: Implement kill switches to disable new logic instantly; provide fallback logic for exception scenarios; support hot config reloads without redeployment.

## Risk rules (categorized, MECE)

### Payload & data size

1. **Avoid unbounded large payloads (P0)**
   - **Why**: Large lists or full-history payloads can blow latency and memory.
   - **Bad**: Request/response DTO carries full history with no pagination or size limit.
   - **Good**: Require pagination/size limits; exclude large fields by default.

2. **Cap order/detail sizes for batch workflows (P0)**
   - **Why**: Unbounded order/detail sets create hot paths and timeouts.
   - **Bad**: A "big order" or import task accepts unlimited detail rows.
   - **Good**: Enforce thresholds; split, paginate, or process in batches.

3. **Stream or page large exports (P1)**
   - **Why**: Exporting full objects without paging exhausts memory.
   - **Bad**: Export API returns all rows without a paging parameter.
   - **Good**: Page/batch exports; use streaming writers.

4. **Do not ignore pagination in export queries (P1)**
   - **Why**: Accepting pageNum/pageSize but querying full data creates hidden OOM and timeout risk.
   - **Bad**: Export handler receives pagination but calls a full-scan query.
   - **Good**: Apply pageNum/pageSize or explicitly document full export with safeguards (limits, streaming).

### Downstream load & call patterns

1. **Avoid high-QPS fan-out to downstreams (P0)**
   - **Why**: Unbounded fan-out can exceed downstream SLA and throttle the system.
   - **Bad**: Tight loop calls downstream without batching or caching.
   - **Good**: Estimate QPS; batch or merge requests; add caching if needed.

2. **Do not call downstreams inside nested loops (P0)**
   - **Why**: Nested calls multiply latency and load unpredictably.
   - **Bad**: For-each item triggers an RPC/MQ/cache call.
   - **Good**: Batch downstream requests or prefetch in bulk.

### Transactions & consistency

1. **Handle distributed transactions explicitly (P0)**
   - **Why**: Cross-system writes can leave data inconsistent.
   - **Bad**: Local DB write followed by RPC/MQ with no compensation.
   - **Good**: Use idempotency + compensation + event-driven design.

2. **Keep transactions small and DB-only (PS)**
   - **Why**: RPC/IO inside transactions increases locks and deadlock risk.
   - **Bad**: Transaction wraps RPC/IO/large loops.
   - **Good**: Minimize scope to DB operations; split where needed.

3. **Define rollback/compensation for downstream failures (P0)**
   - **Why**: Failed downstream operations can leave partial state.
   - **Bad**: Downstream failure has no rollback strategy.
   - **Good**: Provide compensating jobs or replay mechanisms.

4. **Design for eventual consistency when async (P0)**
   - **Why**: Async workflows require repair paths.
   - **Bad**: Event-driven flow without reconciliation or replay.
   - **Good**: Add compensation, reconciliation, and replay support.

5. **Protect against archived-data operations (P0)**
   - **Why**: Operating on archived data can violate business rules.
   - **Bad**: Business action assumes archived data is mutable.
   - **Good**: Define archive rules and allowed operations.

6. **Enforce state consistency across systems (P0)**
   - **Why**: Upstream/downstream state drift causes hard-to-debug defects.
   - **Bad**: Status updates are not coordinated or reconciled.
   - **Good**: Use state machines and reconciliation tasks.

### Concurrency & threading

1. **Ensure recursion has termination and depth limits (P0)**
   - **Why**: Unbounded recursion can overflow or hang.
   - **Bad**: Recursive method with no depth guard.
   - **Good**: Add max depth or convert to iteration.

2. **Configure thread pools explicitly (P0)**
   - **Why**: Default pools and ad-hoc executors are risky in production.
   - **Bad**: Use `Executors` defaults or unbounded queues.
   - **Good**: Set core/max threads, queue size, and rejection policy.

3. **Isolate business async tasks from RPC pools (P0)**
   - **Why**: Shared pools can starve critical threads.
   - **Bad**: Business tasks run on RPC thread pools.
   - **Good**: Use dedicated pools per workload type.

4. **Protect shared mutable state (P0)**
   - **Why**: Concurrent writes without guards corrupt data.
   - **Bad**: Shared state updated with no locks or idempotency.
   - **Good**: Use locks/optimistic versions and reentrancy checks.

5. **Use thread-safe collections in multithreaded code (P0)**
   - **Why**: Non-thread-safe lists/maps can corrupt data.
   - **Bad**: `ArrayList` or `HashMap` shared across threads.
   - **Good**: Use concurrent collections or explicit locking.

6. **Never nest tasks within the same thread pool (P0)**
   - **Why**: Submitting inner tasks to the same executor that runs outer tasks creates a circular wait—outer tasks hold threads waiting for inner tasks, while inner tasks wait for threads held by outer tasks—resulting in deadlock.
   - **Bad**: Outer `CompletableFuture` runs on `asyncServiceExecutor` and calls inner `CompletableFuture.supplyAsync(..., asyncServiceExecutor)` on the same pool; when pool threads are exhausted, both layers block indefinitely.
   - **Good**: Use a separate, dedicated executor for inner tasks; or restructure the workflow to avoid nested submission (e.g., flatten to a single-level parallel execution, or use `thenCompose` / `thenApply` to chain without nesting).

7. **Always release ThreadLocal values (P1)**
   - **Why**: Thread reuse can leak state between requests.
   - **Bad**: `ThreadLocal.set()` without `remove()` in `finally`.
   - **Good**: Clear ThreadLocal in `finally` for pooled threads.

### Distributed locks

1. **Use fine-grained lock keys (P0)**
   - **Why**: Coarse keys reduce concurrency and create contention.
   - **Bad**: Lock key missing business dimensions.
   - **Good**: Include business identifiers in the lock key.

2. **Release distributed locks safely (P0)**
   - **Why**: Incorrect unlock can release someone else's lock.
   - **Bad**: Unlock without token check or non-atomic release.
   - **Good**: Use token + Lua atomic release.

3. **Define lock failure degradation (PS)**
   - **Why**: Redis or lock middleware can fail.
   - **Bad**: Lock failures have no fallback.
   - **Good**: Define fallback behavior or circuit-breakers.

4. **Lock before query when using Redis (PS)**
   - **Why**: Query-before-lock can introduce race conditions.
   - **Bad**: Check whether the lock exists, then acquire it, then run business logic.
   - **Good**: Acquire the lock first, then query state, then run business logic.

### Idempotency & retries

1. **Add idempotency for retryable operations (P0)**
   - **Why**: Retries can duplicate side effects.
   - **Bad**: Retryable API or MQ handler without dedup.
   - **Good**: Use idempotency keys and dedup tables/caches.

2. **Verify downstream supports idempotency (P0)**
   - **Why**: Upstream retries can multiply downstream writes.
   - **Bad**: Call downstream write API with no idempotency key.
   - **Good**: Pass idempotency key and confirm downstream behavior.

3. **Treat retries as behavioral changes (P0)**
   - **Why**: Retries change semantics and load.
   - **Bad**: Enable retries with no idempotency check.
   - **Good**: Ensure method is repeatable or idempotent.

4. **Avoid implicit Dubbo retries (PS)**
   - **Why**: Default retries can amplify load and side effects.
   - **Bad**: Rely on Dubbo default retries without review.
   - **Good**: Configure retries explicitly and validate idempotency.

### RPC timeouts & error handling

1. **Set explicit network timeouts (PS)**
   - **Why**: Default or infinite timeouts can exhaust threads.
   - **Bad**: RPC/HTTP timeout missing or set to 0.
   - **Good**: Configure sensible timeouts and error paths.

2. **Configure RPC timeouts per client/endpoint (PS)**
   - **Why**: Global defaults are often too lax or too strict.
   - **Bad**: Dubbo/Feign/HTTP with no per-client timeout config.
   - **Good**: Set global + per-interface + per-client timeouts.

3. **Do not swallow downstream exceptions (PS)**
   - **Why**: Hidden failures break observability and control flow.
   - **Bad**: Catch and ignore or only log downstream errors.
   - **Good**: Propagate or wrap with context; add fallback if needed.

4. **Apply circuit-breaking and degradation for downstream errors (PS)**
   - **Why**: Downstream failures can cascade.
   - **Bad**: Downstream error is swallowed or silently ignored.
   - **Good**: Use circuit breakers, fallbacks, and clear error propagation.

### Messaging reliability

1. **Prevent producer message loss (PS)**
   - **Why**: Unconfirmed sends can drop messages silently.
   - **Bad**: MQ send without confirmation or transaction.
   - **Good**: Use send confirm; retry or compensate on failure.

2. **Handle consumer retry and idempotency (PS)**
   - **Why**: Consumers can lose or duplicate processing.
   - **Bad**: No retry or dedup for failed consumption.
   - **Good**: Acknowledge correctly; use dead-letter queues and dedup.

3. **Avoid MQ consumption backlog (P0)**
   - **Why**: Backlog delays critical workflows.
   - **Bad**: Consumer throughput below production rate.
   - **Good**: Scale consumers, rate-limit producers, or batch processing.

### Database access & performance

1. **Prevent slow SQL and full scans (PS)**
   - **Why**: Unindexed queries degrade performance.
   - **Bad**: Query on non-index fields or wide-range scans.
   - **Good**: Use indexes; add limits/pagination.

2. **Avoid non-index updates/deletes (PS)**
   - **Why**: Full-table operations can lock and slow the DB.
   - **Bad**: Update/delete without indexed WHERE.
   - **Good**: Use indexed WHERE; batch and limit.

3. **Use primary keys for updates when possible (P2)**
   - **Why**: Non-unique WHERE can update unintended rows.
   - **Bad**: Update with broad non-PK conditions.
   - **Good**: Use PK or enforce unique constraints.

4. **Guard against empty query parameters (PS)**
   - **Why**: Missing parameters can cause full-table queries.
   - **Bad**: WHERE conditions allow null or empty without checks.
   - **Good**: Validate inputs; use dynamic SQL with null checks.

5. **Be explicit about DTS replication delay (P2)**
   - **Why**: Reads may be stale with replication delay.
   - **Bad**: Business logic assumes immediate sync.
   - **Good**: Accept delay or provide backfill/repair strategy.

6. **Reduce lock contention in batch operations (P0)**
   - **Why**: Large batch updates can block hot tables.
   - **Bad**: Massive update/delete in one transaction.
   - **Good**: Shard batches, order locks, and rate-limit.

7. **Match MyBatis parameter types to indexed column types (P0)**
   - **Why**: Type mismatch causes MySQL implicit conversion, which invalidates indexes and triggers full table scans.
   - **Bad**: Mapper method accepts `String` parameter for a column defined as `INT`/`BIGINT` in the database; MySQL converts every row's column value to compare with the string literal, bypassing the index.
   - **Good**: Ensure Java parameter types match database column types exactly (e.g., `Long` for `BIGINT`, `Integer` for `INT`/`TINYINT`). Reference the `resultMap` definitions in mapper XML files (e.g., `<result column="status" jdbcType="TINYINT"/>`) to verify column types and align Mapper interface parameters accordingly.

### Cache & search

1. **Mitigate cache breakdown (PS)**
   - **Why**: Cache misses can spike DB load.
   - **Bad**: Cache miss falls through to DB with no protection.
   - **Good**: Use mutex locks, hot keys, or bloom filters.

2. **Avoid full-text search on MySQL (P2)**
   - **Why**: LIKE searches do not scale for search workloads.
   - **Bad**: Use MySQL LIKE for full-text or listing search.
   - **Good**: Use ES or dedicated search/cache indexes.

### Multi-tenancy & context propagation

1. **Validate tenant isolation on every request (PS)**
   - **Why**: Implicit tenant fields can leak data across tenants.
   - **Bad**: Tenant is read only from context with no validation.
   - **Good**: Validate tenant end-to-end; align request and context.

2. **Do not pass tenant by implicit context (P0)**
   - **Why**: Implicit context can be lost or spoofed.
   - **Bad**: Tenant/warehouse inferred only from context.
   - **Good**: Pass tenant explicitly; validate consistency.

3. **Avoid Dubbo implicit tenant attachments (P1)**
   - **Why**: RPC context can break isolation in async flows.
   - **Bad**: `RpcContext.setAttachment` for tenant propagation.
   - **Good**: Explicit parameters in RPC interfaces.

### API contracts & compatibility

1. **Keep releases backward compatible (P0)**
   - **Why**: Incompatible changes break mixed versions.
   - **Bad**: Remove or change field types without migration.
   - **Good**: Use dual-write/compat layers and gradual rollout.

2. **Handle unknown enum values (P2)**
   - **Why**: Enums evolve and old clients may see new values.
   - **Bad**: Fail on unknown enum.
   - **Good**: Add an `UNKNOWN`/default branch.

3. **Validate enum mappings between systems (P2)**
   - **Why**: Enum conversions can drift between services.
   - **Bad**: Map enums without fallback for unknown values.
   - **Good**: Provide compatibility mapping and defaults.

4. **Ensure RPC generic call types match (P1)**
   - **Why**: Type mismatches cause serialization loss.
   - **Bad**: Generic DTO fields with inconsistent types.
   - **Good**: Keep field types aligned; test serialization.

5. **Return correct result codes (P2)**
   - **Why**: Incorrect codes mislead clients and retries.
   - **Bad**: Return 200 on failure or non-200 on success.
   - **Good**: Align business status with HTTP/Result codes.

6. **Return empty collections, not null (P2)**
   - **Why**: Null collections force defensive checks.
   - **Bad**: Return `null` for list fields.
   - **Good**: Return `Collections.emptyList()`/empty arrays.

7. **Dubbo API methods must not be overloaded (P0)**
   - **Why**:  APM cannot distinguish traffic between overloaded methods.
   - **Bad**: Using method overloading in Dubbo APIs.
   - **Good**: Avoid overloading in Dubbo APIs; define separate methods with distinct names.

### Data validation & correctness

1. **Validate critical message fields (P1)**
   - **Why**: Missing fields can break consumers or workflows.
   - **Bad**: Core message fields are not validated.
   - **Good**: Enforce required fields and defaulting rules.

2. **Avoid NPE-prone chained calls (P1)**
   - **Why**: Deep chaining hides null risk.
   - **Bad**: `get().get()` with no null checks.
   - **Good**: Validate external responses and collection nulls.

3. **Do not use only null checks for collections (P1)**
   - **Why**: Empty collections are often invalid too.
   - **Bad**: Check `list != null` but ignore emptiness.
   - **Good**: Check `isEmpty()` when required.

4. **Avoid empty-vs-blank mistakes (P2)**
   - **Why**: `" "` should be treated as empty in many cases.
   - **Bad**: Use `isEmpty()` for user input validation.
   - **Good**: Use `isBlank()` where whitespace is invalid.

5. **Use BigDecimal for money (P1)**
   - **Why**: `double/float` lose precision.
   - **Bad**: Store/compute money in `double`.
   - **Good**: Use `BigDecimal` with scale and rounding.

6. **Ensure business logic conditions are tight (P1)**
   - **Why**: Over-broad conditions expand impact scope.
   - **Bad**: If conditions match more states than intended.
   - **Good**: Define boundary conditions and error paths.

7. **Avoid unordered data dependencies (P2)**
   - **Why**: JSON/sets are unordered by default.
   - **Bad**: Logic depends on map/JSON iteration order.
   - **Good**: Sort data or use ordered structures.

8. **Guard MyBatis WHERE against nulls (P1)**
   - **Why**: Null parameters can generate unintended SQL.
   - **Bad**: `WHERE col = #{param}` when `param` may be null.
   - **Good**: Use `<if>` checks and dynamic SQL.

9. **Use unique names for OSS files (P1)**
   - **Why**: Non-unique names overwrite data.
   - **Bad**: Filenames derived only from date or business id.
   - **Good**: Include unique ID or random suffix.

10. **Avoid type erasure in JSON deserialization (P2)**
   - **Why**: Generic types can drop fields on deserialize.
   - **Bad**: Deserialize without `TypeReference`.
   - **Good**: Use `TypeReference` for generic DTOs.

### Dependency & environment management

1. **Resolve Spring circular dependencies explicitly (P0)**
   - **Why**: Circular dependencies mask design issues.
   - **Bad**: `A -> B -> A` with `@Lazy` as a band-aid.
   - **Good**: Refactor to break cycles; keep dependencies acyclic.

2. **Avoid env key collisions with reserved names (PS)**
   - **Why**: Collisions can shadow system defaults.
   - **Bad**: Env var name conflicts with system keywords.
   - **Good**: Follow naming conventions and avoid reserved keys.

3. **Do not load config in static initializers (P0)**
   - **Why**: Static init blocks block reloads and startup.
   - **Bad**: `static { loadConfig(); }`.
   - **Good**: Use lazy or managed config loading.

4. **Prefer configuration over hard-coded constants (P2)**
   - **Why**: Hard-coded values reduce flexibility and safety.
   - **Bad**: Business values embedded in code.
   - **Good**: Use config or centralized enums.

5. **Keep environment-specific logic consistent (P1)**
   - **Why**: Domestic/overseas forks drift over time.
   - **Bad**: Branches diverge without feature flags.
   - **Good**: Use env flags and consistent pathways.

### Logging & observability

1. **Avoid oversized logs (P2)**
   - **Why**: Logging full payloads leaks data and adds noise.
   - **Bad**: Log full request/response objects.
   - **Good**: Log identifiers/summary; redact sensitive fields.

2. **Do not swallow exceptions (PS)**
   - **Why**: Silent failures hide defects and break monitoring.
   - **Bad**: Empty catch or log-only error handling.
   - **Good**: Propagate, alert, or handle with clear fallback.

### Testing discipline

1. **Avoid mocks that skip failure paths (P2)**
   - **Why**: Forced-success mocks hide real error handling.
   - **Bad**: Mock always returns success so exceptions never surface.
   - **Good**: Include failure cases in tests or manual plans.

