#!/usr/bin/python

import os
import pathlib
import textwrap

from ansible.module_utils.basic import AnsibleModule

MODULE_NAME = "ansible-check-notify"


def get_systemd_config_dir():
    config_dir = os.environ.get("XDG_CONFIG_DIR") or pathlib.Path(
        os.environ["HOME"], ".config"
    )
    return pathlib.Path(config_dir, "systemd", "user")


SYSTEMD_CONFIG_DIR = get_systemd_config_dir()


def util_format(lines):
    return "\n".join([textwrap.dedent(line) for line in lines.strip().split("\n")])


def make_safe_cmd(cmd):
    return cmd.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")


def make_cmd_notify_send(*, title, body):
    body = "\n" + body if body is not None else ""
    return f'notify-send "{title}" "{body}"'


def template_systemd_unit_files(*, id, cmd, timer_dict):
    template_service = util_format(
        f"""
    # Managed by {MODULE_NAME}
    #
    [Unit]
    Description={MODULE_NAME}: {id} service

    [Service]
    ExecStart=/bin/bash -c "{make_safe_cmd(cmd)}"

    [Install]
    WantedBy=multi-user.target
    """
    )

    timer = "\n".join([f"{key}={value}" for key, value in timer_dict.items()])
    template_timer = util_format(
        f"""
    # Managed by {MODULE_NAME}
    #
    [Unit]
    Description={MODULE_NAME}: {id} timer

    [Install]
    WantedBy=timers.target

    [Timer]
    {timer}
    """
    )
    return template_service, template_timer


def create_systemd_unit_files(
    path_service, template_service, path_timer, template_timer
):
    try:
        path_service.write_text(template_service)
        path_timer.write_text(template_timer)
    except Exception as exc:
        path_service.unlink(missing_ok=True)
        path_timer.unlink(missing_ok=True)
        raise (exc)


def enable_systemd_timer(module, unit_name):
    cmd = f"systemctl --user enable --now {unit_name}.timer"
    module.run_command(cmd)


def main():
    module = AnsibleModule(
        argument_spec={
            "id": {"type": "str", "required": True},
            "condition": {"type": "str", "required": True},
            "message": {"type": "str"},
            "timer": {"type": "dict"},
        },
        supports_check_mode=True,
    )

    if module.get_bin_path("systemctl") is None:
        module.fail_json(msg="systemctl not found")

    if module.get_bin_path("notify-send") is None:
        module.fail_json("msg=notify-send not found")

    arg_id = module.params["id"]
    arg_condition = module.params["condition"]
    arg_message = module.params["message"]
    arg_timer = module.params["timer"]

    cmd_rc, _, _ = module.run_command(arg_condition, use_unsafe_shell=True)
    if cmd_rc != 0:
        module.exit_json(changed=False, msg="")

    notify_cmd = make_cmd_notify_send(
        title=f"[{MODULE_NAME}] {arg_id}", body=arg_message
    )

    if arg_timer is None:
        module.run_command(notify_cmd, use_unsafe_shell=True)
        module.exit_json(changed=True, msg="", diff="")

    unit_name = f"{MODULE_NAME}_{arg_id}"
    path_service = SYSTEMD_CONFIG_DIR.joinpath(f"{unit_name}.service")
    path_timer = SYSTEMD_CONFIG_DIR.joinpath(f"{unit_name}.timer")
    template_service, template_timer = template_systemd_unit_files(
        id=arg_id, cmd=notify_cmd, timer_dict=arg_timer
    )
    # FIXME add check mechanism for change and diff.
    # def is_timer_unit_active(module, unit_name):
    #     rc, _, _ = module.run_command(
    #       f'systemctl --user is-active {unit_name}.timer'
    # )
    #     return rc == 0
    # if is_timer_unit_active(module, unit_name):
    #     module.exit_json(changed=False, msg='')
    # if path_service.exists() and path_timer.exists():
    #     is_service_file_equal =
    #         module.sha256(path_service) == module.sha256(template_service)
    #     is_timer_file_equal =
    #         module.sha256(path_timer) == module.sha256(template_timer)
    create_systemd_unit_files(
        path_service, template_service, path_timer, template_timer
    )
    enable_systemd_timer(module, unit_name)
    module.exit_json(changed=True, msg="", diff="")


if __name__ == "__main__":
    main()
