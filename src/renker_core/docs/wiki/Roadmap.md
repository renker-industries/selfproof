# Roadmap — 12 months

## Months 1–3: Foundation

**Rencora**
- [ ] Capability/permission system (schema, storage, checking)
- [ ] Sandboxing for tool execution
- [ ] Audit log (append-only, queryable)
- [ ] First prompt-injection test suite

**RenkerVault**
- [ ] Protocol specification (written, versioned)
- [ ] Threat model (explicitly documented, with out-of-scope)
- [ ] Test vectors for the crypto layer
- [ ] Fuzzing setup
- [ ] External or structured internal crypto review

**Continuum**
- [ ] Define a benchmark suite
- [ ] Establish baselines
- [ ] Reproducible experiment pipeline
- [ ] Evaluation framework (incl. evidence-status fields)

*Definition of Done (month 3):* All three repos have a runnable, testable minimal system — not "finished", but demonstrable.

## Months 4–6: Stabilization
- [ ] Rencora: permission system and sandbox work together
- [ ] RenkerVault: stable protocol v1, frozen for external reviews
- [ ] Continuum: first reproducible research benchmarks published

## Months 7–9: Test reality
- [ ] Real external users (not friends, not just GitHub stars)
- [ ] People with real problems of their own test on their own use cases
- [ ] Systematically collect: where does usage break off? What would someone pay for? What gets ignored?

## Months 10–12: Set direction
- [ ] Evaluation: which part does someone actually pay for?
- [ ] Derive the focus for year 2 (likely Rencora/agent security as the core)

---

### renker-core — immediate next step (month-1 milestone)
- [ ] Identity, Permissions, Audit as runnable, comment-free modules (per Vision 5.1/5.2)
- [ ] Implement the permission-object schema
- [ ] Append-only audit log with hash chain
