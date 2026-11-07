# Planted defects (sealed until the end of P01)

These three defects were written into the starting code on purpose (commit `4af236b`), so that the reviewers had something real to find. This file was committed only after every design review and the gate had run, so no reviewer could see it.

The builder (the session that wrote the plan and the code) knew about them and deliberately left them out of the first plan. Nothing in plan revision 1 mentions them: the only route to a fix was a reviewer finding them.

| # | Where (starting code) | Defect | Consequence |
|---|---|---|---|
| D1 | `signup/store.py` (`exists` / `add`), fed by `signup/validator.py:validate_email` | The duplicate-email check is case-sensitive: `Bo@Example.com` and `bo@example.com` are different keys. | One inbox can hold two accounts; a per-email limit could be bypassed by changing letter case. |
| D2 | `signup/validator.py:validate_password` | Off by one: `len(password) <= MIN_PASSWORD_LENGTH` rejects a password of exactly 8 characters, although 8 is the stated minimum. | Honest users with an 8-character password are refused; with a failed-attempt limit, they could even be locked out. |
| D3 | `signup/service.py:signup` | Not fail-safe: `welcome_sent` is set to `True` after the mailer raised, and also when no mailer is configured. | The system records a welcome email as sent when none was sent (a silent failure). |
