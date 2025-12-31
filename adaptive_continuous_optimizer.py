import os
import subprocess
import shutil
import time
import concurrent.futures
import random

# Configuration
INITIAL_INPUT = "submission_current_best.csv" # Continue from where we left off
CURRENT_BEST = "submission_current_best.csv"
OPTIMIZER_EXE = "./ultimate_optimizer_serial"
BASE_ITERS = 40000 
BASE_RESTARTS = 6 
NUM_WORKERS = 8 

def optimize_group(n, input_file, t_scale):
    group_out_csv = f"temp_adaptive_{n}.csv"
    
    env = os.environ.copy()
    env["GROUP_NUMBER"] = str(n)
    
    cmd = [
        OPTIMIZER_EXE,
        "-i", input_file,
        "-o", group_out_csv,
        "-n", str(BASE_ITERS),
        "-r", str(BASE_RESTARTS),
        "-t", str(t_scale)
    ]
    
    try:
        subprocess.run(cmd, env=env, capture_output=True, text=True)
        return n, True, group_out_csv
    except Exception as e:
        print(f"[Group {n}] Error: {e}")
        return n, False, None

def merge_results(results, base_file, output_file):
    def read_dataset(fname):
        d = {}
        try:
            with open(fname, 'r') as f:
                next(f) # header
                for line in f:
                    parts = line.split(',')
                    if len(parts) < 1: continue
                    id_str = parts[0]
                    if '_' not in id_str: continue
                    grp = int(id_str.split('_')[0])
                    if grp not in d: d[grp] = []
                    d[grp].append(line)
        except: pass
        return d

    base_data = read_dataset(base_file)
    count = 0
    
    for n, _, fname in results:
        if fname and os.path.exists(fname):
            temp_data = read_dataset(fname)
            if n in temp_data:
                base_data[n] = temp_data[n]
                count += 1
            try:
                os.remove(fname)
            except OSError:
                pass

    with open(output_file, 'w') as f:
        f.write("id,x,y,deg\n")
        import collections
        od = collections.OrderedDict(sorted(base_data.items()))
        for grp, lines in od.items():
            for line in lines:
                f.write(line)
    return count

def get_total_score(filename):
    try:
        ret = subprocess.run(["./verify_score", filename], capture_output=True, text=True)
        return float(ret.stdout.strip())
    except:
        return 999999.0

def main():
    if not os.path.exists(INITIAL_INPUT):
        if os.path.exists("inshalalh_ultimate.csv"):
             shutil.copy("inshalalh_ultimate.csv", CURRENT_BEST)
        else:
            print("No input file found!")
            return

    best_score = get_total_score(CURRENT_BEST)
    print(f"Starting ADAPTIVE Optimization Loop.")
    print(f"Current Best Score: {best_score:.15f}")
    
    round_num = 1
    stagnant_rounds = 0
    current_temp = 1.0
    
    while True:
        # Adjustment Logic
        if stagnant_rounds > 2:
            current_temp += 0.5 
            print(f"⚠️ Stagnant for {stagnant_rounds} rounds. HEATING UP! t_scale={current_temp:.2f}")
        else:
            current_temp = max(1.0, current_temp - 0.2) # Cool down slowly
        
        # Max temp cap
        if current_temp > 5.0:
            print("Temp too high, resetting to 1.5")
            current_temp = 1.5
            
        print(f"\n=== ROUND {round_num} (T={current_temp:.2f}) ===")
        round_start = time.time()
        
        groups = list(range(1, 201))
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            future_to_n = {executor.submit(optimize_group, n, CURRENT_BEST, current_temp): n for n in groups}
            
            processed = 0
            for future in concurrent.futures.as_completed(future_to_n):
                processed += 1
                try:
                    res = future.result()
                    results.append(res)
                except: pass
                if processed % 50 == 0:
                    print(f"Progress: {processed}/200...")
        
        candidate_file = f"temp_round_{round_num}.csv"
        merge_results(results, CURRENT_BEST, candidate_file)
        
        new_score = get_total_score(candidate_file)
        improvement = best_score - new_score
        
        if improvement > 1e-10:
            print(f"🔥 Round {round_num} IMPROVED: {best_score:.15f} -> {new_score:.15f}")
            print(f"   Gain: {improvement:.15f}")
            shutil.copy(candidate_file, CURRENT_BEST)
            best_score = new_score
            stagnant_rounds = 0
            
            # Save milestone
            if improvement > 1e-5:
                 shutil.copy(candidate_file, f"submission_adaptive_{round_num}_{new_score:.6f}.csv")
        else:
            print(f"Round {round_num} result: {new_score:.15f} (No Improvement)")
            stagnant_rounds += 1
            if os.path.exists(candidate_file):
                os.remove(candidate_file)
                
        print(f"Round time: {time.time() - round_start:.2f}s")
        round_num += 1

if __name__ == "__main__":
    main()
