import os
import argparse
import subprocess

def main(args):
    os.makedirs(args.output_path, exist_ok=True)

    patient_ids = [
        d for d in os.listdir(args.dicom_path)
        if os.path.isdir(os.path.join(args.dicom_path, d)) and d.isdigit()
    ]

    success_list = []
    fail_list = []
    skip_list = []

    for pid in sorted(patient_ids):
        in_dir = os.path.join(args.dicom_path, pid, "SWIp_M")
        if not os.path.isdir(in_dir):
            print(f"[WARNING] {pid}: Input folder does not exist -> {in_dir}")
            skip_list.append(pid)
            continue

        output_file = os.path.join(args.output_path, f"{pid}.nii.gz")

        cmd = [
            "dcm2niix",
            "-o", args.output_path,
            "-f", pid,
            "-z", "y",
            "-b", "n",
            "-v", "1",
            in_dir,
        ]

        print(f"[RUN] {pid}: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"[OK]  {pid} -> {output_file}")
            success_list.append(pid)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] {pid}: Conversion failed (code={e.returncode})")
            print(e.stdout or "")
            print(e.stderr or "")
            fail_list.append(pid)

    # --- Summary report ---
    print("\n========== SUMMARY ==========")
    print(f"Total cases: {len(patient_ids)}")
    print(f"  ✅ Success: {len(success_list)}")
    print(f"  ❌ Failed : {len(fail_list)}")
    print(f"  ⚠️  Skipped: {len(skip_list)}")

    if success_list:
        print("\n[Successful IDs]")
        print(", ".join(success_list))

    if fail_list:
        print("\n[Failed IDs]")
        print(", ".join(fail_list))

    if skip_list:
        print("\n[Skipped IDs]")
        print(", ".join(skip_list))

    print("=============================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dicom_path", type=str, required=True)
    parser.add_argument("-o", "--output_path", type=str, required=True)
    args = parser.parse_args()
    main(args)
