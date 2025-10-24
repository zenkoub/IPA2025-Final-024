import subprocess

router_name_map = {
    "10.0.15.61": "R1",
    "10.0.15.62": "R2",
    "10.0.15.63": "R3",
    "10.0.15.64": "R4",
    "10.0.15.65": "R5",
}

def showrun(studentID, router_ip):
    router_name = router_name_map.get(router_ip, router_ip)
    filename = f"show_run_{studentID}_{router_name}.txt"

    command = [
        "ansible-playbook",
        "playbook.yaml",
        "--extra-vars",
        f"target={router_ip} output_file={filename}"
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    print("STDOUT:", stdout)
    print("STDERR:", stderr)

    if "failed=0" in stdout:
        return filename
    else:
        return "Error: Ansible"

def configure_motd(studentID, router_ip, motd_text):
    router_name = router_name_map.get(router_ip, router_ip)

    command = [
        "ansible-playbook",
        "motd_playbook.yaml",
        "-e", f"motd_text={motd_text}",
        "-l", router_ip
    ]

    print("Running command:", " ".join(command))

    result = subprocess.run(command, capture_output=True, text=True)
    
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    if "failed=0" in result.stdout and "unreachable=0" in result.stdout:
        return f"Ok: success for student {studentID} on {router_name}"
    else:
        return f"Error: Ansible for student {studentID} on {router_name}"