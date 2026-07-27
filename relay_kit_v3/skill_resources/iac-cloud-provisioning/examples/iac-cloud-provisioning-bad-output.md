# iac-cloud-provisioning Weak Output Anti-Example

Request: review an infrastructure change, read the plan diff, and flag any stateful replace before apply

Weak answer:

This looks like `iac-cloud-provisioning`, so apply the standard fix and it should be fine.

Why this fails:

- No file path from `a Terraform repo with modules, a remote state backend, an environments folder, and a plan CI job` was inspected.
- No symbol such as `aws_db_instance` was confirmed.
- No proof surface was named for `plan diff`.
- It blurs verified evidence and inference, which is how overclaim slips back in.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
