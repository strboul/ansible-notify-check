# ansible-notify-check

[Ansible module](https://docs.ansible.com/ansible/2.10/dev_guide/developing_locally.html#modules-and-plugins-what-is-the-difference)
to send notifications periodically. Ideal for desktop environment setups.

The module uses [notify-send](https://man.archlinux.org/man/notify-send.1.en)
to send the notification. Also, with `timer` part with
[systemd-timer](https://man.archlinux.org/man/core/systemd/systemd.timer.5.en),
it can send time-based notifications.

## Usage

| parameter             | required | type | description               |
|-----------------------|----------|------|---------------------------|
| `id`                  | yes      | str  | unique service and timer id. |
| `condition`           | no       | str  | condition to trigger this check. If condition field exists and if it's a truthy value, the check runs. |
| `message`             | no       | str  | message to display in the notifier. The bash variables are expanded.  |
| `options`             | no       | dict | [notify-send options](https://man.archlinux.org/man/notify-send.1.en#OPTIONS). |
| `options.urgency`     | no       | str  | Specifies the urgency level (low, normal, critical).
| `options.icon`        | no       | str  | icon file name from the locations `$HOME/.icons`, `$HOME/.local/share/icons`, `/usr/local/share/icons`, `/usr/share/icons`. |
| `options.expire_time` | no       | int  | duration in milliseconds for the notification to appear on screen. |
| `timer`               | no       | dict | a dictionary to define [systemd-timer options](https://man.archlinux.org/man/core/systemd/systemd.timer.5.en#OPTIONS). |


## Examples

```yaml
- name: Check condition and notify
  strboul.notify.check:
    id: test
    condition: "[[ 1 == 1 ]]"
    message: |
      This notification is shown 1 minute after the boot and then every 10
      minutes after the first run.

      You can use shell parameter expansion.
      Lang is "$LANG".
      Now is "$(date)".

      Also ansible variables.
      Home is {{ ansible_env.HOME }}.
    options:
      urgency: critical
      icon: user-info
    timer:
      OnBootSec=1min
      OnUnitActiveSec=10min
```

## Installation

```sh
ansible-galaxy install https://github.com/strboul/ansible-notify-check.git
```

## Development

<details>

#### Run tests

```sh
ansible-galaxy collection build .
ansible-galaxy collection install strboul-notify-*.tar.gz
ansible-playbook tests/*
```

#### Debugging

```sh
python plugins/modules/check.py tests/args.json
```

- <https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html>

- <https://docs.ansible.com/ansible/latest/dev_guide/debugging.html>

</details>
