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
    print(result.stdout)
    print(result.stderr) # Print stderr for debugging

    if "skipping: no hosts matched" in result.stdout:
        return "Error: No matching host in inventory"
    elif "failed=" in result.stdout:
        return "Error: Ansible"
    else:
        return filename
