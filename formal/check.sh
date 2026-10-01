#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TLA_DIR="${HOME}/.cache/tla"
JAR="${TLA_DIR}/tla2tools-1.7.4.jar"
URL="https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar"
SHA256="936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88"

mkdir -p "${TLA_DIR}"

sha256_file() {
  local path="$1"
  if command -v sha256sum >/dev/null; then
    sha256sum "${path}" | awk '{print $1}'
  else
    shasum -a 256 "${path}" | awk '{print $1}'
  fi
}

download_jar() {
  tmp="${JAR}.tmp"
  curl -fsSL "${URL}" -o "${tmp}"
  got="$(sha256_file "${tmp}")"
  if [[ "${got}" != "${SHA256}" ]]; then
    rm -f "${tmp}"
    echo "tla2tools sha256 mismatch: got ${got}" >&2
    exit 1
  fi
  mv "${tmp}" "${JAR}"
}

if [[ ! -f "${JAR}" ]]; then
  download_jar
else
  got="$(sha256_file "${JAR}")"
  if [[ "${got}" != "${SHA256}" ]]; then
    rm -f "${JAR}"
    download_jar
    got="$(sha256_file "${JAR}")"
    if [[ "${got}" != "${SHA256}" ]]; then
      echo "tla2tools sha256 mismatch after redownload: got ${got}" >&2
      exit 1
    fi
  fi
fi

run_tlc() {
  local cfg="$1"
  local out="$2"
  # run on a copy in a temp directory: TLC writes its state and, on an error, a trace spec next to it
  local work
  work="$(mktemp -d)"
  cp "${ROOT}/formal/render_requests.tla" "${work}/"
  cp "${cfg}" "${work}/check.cfg"
  local status=0
  (cd "${work}" && java -XX:+UseParallelGC -Xmx4g -cp "${JAR}" tlc2.TLC -workers 4 -metadir "${work}/states" -config check.cfg render_requests.tla) >"${out}" 2>&1 || status=$?
  rm -rf "${work}"
  return "${status}"
}

states_from() {
  sed -n 's/^\([0-9][0-9]*\) states generated.*/\1/p; s/.*states generated: \([0-9][0-9]*\).*/\1/p' "$1" | tail -n 1
}

seconds_from() {
  sed -n 's/.*Finished in \([0-9][0-9]*\)s.*/\1/p' "$1" | tail -n 1
}

result_from() {
  local out="$1"
  if grep -q "Model checking completed. No error has been found" "${out}"; then
    echo "pass"
  elif grep -q "Deadlock reached" "${out}"; then
    echo "deadlock"
  elif grep -q "Invariant .* is violated" "${out}"; then
    sed -n 's/.*Invariant \(.*\) is violated.*/\1/p' "${out}" | tail -n 1
  else
    echo "error"
  fi
}

check_one() {
  local name="$1"
  local cfg="$2"
  local expected="$3"
  local out
  out="$(mktemp)"
  local status=0
  run_tlc "${cfg}" "${out}" || status=$?
  local got states seconds
  got="$(result_from "${out}")"
  states="$(states_from "${out}")"
  seconds="$(seconds_from "${out}")"
  states="${states:-?}"
  seconds="${seconds:-?}"
  printf '%s expected=%s got=%s states=%s seconds=%s\n' "${name}" "${expected}" "${got}" "${states}" "${seconds}"
  if [[ "${expected}" == "pass" ]]; then
    if [[ "${status}" -ne 0 || "${got}" != "pass" ]]; then
      cat "${out}" >&2
      rm -f "${out}"
      exit 1
    fi
  else
    if [[ "${got}" != "${expected}" ]]; then
      cat "${out}" >&2
      rm -f "${out}"
      exit 1
    fi
  fi
  rm -f "${out}"
}

check_one "render_requests.cfg" "${ROOT}/formal/render_requests.cfg" "pass"
check_one "no_closer.cfg" "${ROOT}/formal/no_closer.cfg" "pass"
check_one "budget.cfg" "${ROOT}/formal/budget.cfg" "pass"
check_one "effect_calls_close.cfg" "${ROOT}/formal/effect_calls_close.cfg" "pass"
check_one "two_closers.cfg" "${ROOT}/formal/two_closers.cfg" "pass"
check_one "cleanup_calls_close.cfg" "${ROOT}/formal/cleanup_calls_close.cfg" "pass"
check_one "closer_holds_user_lock.cfg" "${ROOT}/formal/closer_holds_user_lock.cfg" "deadlock"
check_one "budget_reachable.cfg" "${ROOT}/formal/budget_reachable.cfg" "NoTooMany"

check_one "mutations/blocking_request.cfg" "${ROOT}/formal/mutations/blocking_request.cfg" "deadlock"
check_one "mutations/element_before_clear.cfg" "${ROOT}/formal/mutations/element_before_clear.cfg" "NoLostRequest"
check_one "mutations/no_look_again.cfg" "${ROOT}/formal/mutations/no_look_again.cfg" "NoLostRequest"
check_one "mutations/read_before_mark.cfg" "${ROOT}/formal/mutations/read_before_mark.cfg" "NoLostRequest"
check_one "mutations/close_no_own_check.cfg" "${ROOT}/formal/mutations/close_no_own_check.cfg" "deadlock"
check_one "mutations/close_no_closing_check.cfg" "${ROOT}/formal/mutations/close_no_closing_check.cfg" "deadlock"
check_one "mutations/close_no_recheck.cfg" "${ROOT}/formal/mutations/close_no_recheck.cfg" "TeardownOnce"
check_one "mutations/limit_reset.cfg" "${ROOT}/formal/mutations/limit_reset.cfg" "BoundedPasses"
check_one "mutations/read_errors_after_release.cfg" "${ROOT}/formal/mutations/read_errors_after_release.cfg" "ErrorsReadUnderLock"
