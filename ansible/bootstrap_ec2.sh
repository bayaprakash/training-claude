#!/usr/bin/env bash
# Run ON the EC2 host as root (Lab 12).
set -euo pipefail

echo "==> Installing Ansible and dependencies (no playbook yet)"
if command -v apt-get >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -y
  apt-get install -y ansible git python3 python3-pip python3-venv
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y ansible git python3 python3-pip
elif command -v yum >/dev/null 2>&1; then
  yum install -y ansible git python3 python3-pip
else
  echo "Unsupported package manager" >&2
  exit 1
fi

ansible --version | head -n 2

echo "==> Writing /root/ansible"
mkdir -p /root/ansible

cat > /root/ansible/ansible.cfg << 'EOF'
[defaults]
inventory = inventory.ini
host_key_checking = False
interpreter_python = auto_silent
retry_files_enabled = False
EOF

cat > /root/ansible/inventory.ini << 'EOF'
[monitoring]
127.0.0.1 ansible_user=root ansible_ssh_pass=CHANGE_ME ansible_python_interpreter=/usr/bin/python3 ansible_connection=local

[monitoring:vars]
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
EOF

cat > /root/ansible/deploy_monitoring.yml << 'EOF'
---
- name: Deploy InfraWatch monitoring app from existing GitHub repo
  hosts: monitoring
  become: true
  vars:
    app_repo: "https://github.com/bayaprakash/training-claude.git"
    app_dir: /opt/monitoring_app
    app_port: 5095
    app_bind: "0.0.0.0"

  tasks:
    - name: Install OS packages
      ansible.builtin.package:
        name:
          - git
          - python3
          - python3-pip
          - python3-venv
        state: present

    - name: Ensure app directory exists
      ansible.builtin.file:
        path: "{{ app_dir }}"
        state: directory
        mode: "0755"

    - name: Clone or update application repository
      ansible.builtin.git:
        repo: "{{ app_repo }}"
        dest: "{{ app_dir }}"
        version: main
        force: true
        update: true

    - name: Create Python virtualenv
      ansible.builtin.command:
        cmd: python3 -m venv {{ app_dir }}/.venv
        creates: "{{ app_dir }}/.venv/bin/python"

    - name: Install Python dependencies
      ansible.builtin.pip:
        requirements: "{{ app_dir }}/requirements.txt"
        virtualenv: "{{ app_dir }}/.venv"

    - name: Ensure .env exists from example
      ansible.builtin.copy:
        src: "{{ app_dir }}/.env.example"
        dest: "{{ app_dir }}/.env"
        remote_src: true
        force: false
        mode: "0600"

    - name: Install systemd unit for InfraWatch
      ansible.builtin.copy:
        dest: /etc/systemd/system/infrawatch.service
        mode: "0644"
        content: |
          [Unit]
          Description=InfraWatch Flask monitoring demo
          After=network.target

          [Service]
          Type=simple
          WorkingDirectory={{ app_dir }}
          Environment=PORT={{ app_port }}
          Environment=FLASK_ENV=development
          EnvironmentFile=-{{ app_dir }}/.env
          ExecStart={{ app_dir }}/.venv/bin/python -c "import os; from app.app import create_app; create_app().run(host='{{ app_bind }}', port=int(os.environ.get('PORT','{{ app_port }}')), debug=False, use_reloader=False)"
          Restart=on-failure
          RestartSec=3

          [Install]
          WantedBy=multi-user.target

    - name: Reload systemd daemon
      ansible.builtin.systemd:
        daemon_reload: true

    - name: Enable and start InfraWatch service
      ansible.builtin.systemd:
        name: infrawatch
        enabled: true
        state: started

    - name: Wait for health endpoint
      ansible.builtin.uri:
        url: "http://127.0.0.1:{{ app_port }}/health"
        method: GET
        status_code: 200
      register: health
      retries: 15
      delay: 2
      until: health.status == 200

    - name: Show health response
      ansible.builtin.debug:
        var: health.json
EOF

cd /root/ansible
echo "==> Dry-run"
ansible-playbook deploy_monitoring.yml --check || true

echo "==> Apply"
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.ini deploy_monitoring.yml

echo "==> Verify"
curl -sS http://127.0.0.1:5095/health || true
echo
systemctl is-active infrawatch || true
echo "==> Lab 12 bootstrap complete"
