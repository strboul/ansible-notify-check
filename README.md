# ansible-check-notify

[Ansible module](https://docs.ansible.com/ansible/2.10/dev_guide/developing_locally.html#modules-and-plugins-what-is-the-difference)
to send notifications periodically. Ideal for desktop environment setups.

The module uses [notify-send](https://man.archlinux.org/man/notify-send.1.en)
to send the notification. Also, with `timer` part with
[systemd-timer](https://man.archlinux.org/man/core/systemd/systemd.timer.5.en),
it can send time-based notifications.

## Usage

| parameter | required | type | description |
|-----------|----------|------|-------------|
| id        | yes      | str  | unique service and timer id. |
| condition | yes      | str  | condition to trigger this check. If condition is a truthy value, the check runs. |
| message   | no       | str  | message to display in the notifier. The bash variables are expanded.  |
| timer     | no       | dict | an object to define [systemd-timer options](https://man.archlinux.org/man/core/systemd/systemd.timer.5.en#OPTIONS). |


## Examples

```yaml
- name: Check condition and notify
  strboul.ansible_check_notify.main:
    id: ssh
    condition: "[[ 1 == 1 ]]"
    message: |
      This runs 1 minute after the machine is booted up.

      You can use shell parameter expansion.
      Lang is "$LANG".
      Now is "$(date)".

      Also ansible variables.
      Home is {{ ansible_env.HOME }}.
    timer:
      OnBootSec: 1m
      Persistent: true
```

## Installation

```sh
ansible-galaxy install https://github.com/strboul/ansible-check-notify.git
```

## Development

<details>

Run tests.

```sh
ansible-galaxy collection build .
ansible-galaxy collection install strboul-ansible_check_notify-*.tar.gz
ansible-playbook tests/*
ansible-galaxy collection build --force . && ansible-galaxy collection install --force strboul-ansible_check_notify-*.tar.gz # FIXME
```

Debugging.

```sh
python plugins/modules/main.py tests/args.json
```

<https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html>
<https://docs.ansible.com/ansible/latest/dev_guide/debugging.html>

</details>
