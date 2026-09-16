# License

Copyright © 2023-present, [D.AT Analytics, LLC](https://d.at/).
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

---

## Modifications

This project is a fork of [ExceptBot](https://github.com/geneffects/exceptbot),
originally created by Brian Risk and D.AT Analytics, LLC.

Modifications Copyright © 2025, Taha Zarei.

The following changes were made to the original work:

- Converted HTML views to Django REST Framework API endpoints
- Replaced `auth.User` with `settings.AUTH_USER_MODEL` for custom user model support
- Added new model fields: `http_method`, `status_code`, `source`, `ip_address`, `user_agent`, `request_data`, `resolution_note`
- Added source detection via the `X-Client-Type` header
- Added sensitive data masking for request bodies
- Added singleton pattern for `AppSettings` with `get_solo()` method
- Added `mark_resolved()` method to `ExceptionLog`
- Removed form-based UI and HTML templates