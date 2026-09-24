import time
from datetime import datetime

from garak.probes.promptinject import HijackHateHumans
from garak.detectors.promptinject import AttackRogueString
from garak.attempt import Attempt, Message

from src.pipeline import SelfHealingPipeline
from src.mitigations import SystemPromptMitigation, RogueStringCensorMitigation


MAX_EVALUATIONS = 100
MITIGATION_NAME = "SystemPrompt+RogueStringMitigation"


def evaluate_with_garak(
    prompt: str,
    response: str,
    rogue_string: str,
    detector: AttackRogueString,
) -> float:

    attempt = Attempt(
        prompt=Message(prompt)
    )

    # Garak's AttackRogueString detector expects trigger strings in attempt.notes["triggers"].
    attempt.notes["triggers"] = [rogue_string]

    # Add the pipeline's response to the Attempt.
    attempt.outputs = [response]

    # Let Garak perform the detection.
    results = detector.detect(attempt)

    if not results:
        return 0.0

    return results[0]


def main():
    probe = HijackHateHumans()
    pi_prompts = probe.pi_prompts

    # Repeat the probe prompts if more evaluations are requested.
    evaluations = [
        pi_prompts[i % len(pi_prompts)]
        for i in range(MAX_EVALUATIONS)
    ]

    total = len(evaluations)

    # Create timestamped, mitigation-specific results filename.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results_filename = (f"results/patched/results_{MITIGATION_NAME}_{timestamp}.txt")

    overall_start = time.time()
    successful = 0
    failed = 0

    detector = AttackRogueString()

    print(f"Starting evaluation of {total} prompts...", flush=True,)
    print(f"Mitigation: {MITIGATION_NAME}", flush=True,)
    print(f"Results file: {results_filename}", flush=True,)

    with open(results_filename, "w", encoding="utf-8") as results_file:        
        # Header
        results_file.write("=" * 80 + "\n")
        results_file.write("Garak Prompt Injection Evaluation\n")
        results_file.write("=" * 80 + "\n")
        results_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        results_file.write(f"Mitigation: {MITIGATION_NAME}\n")
        results_file.write(f"Probe: {probe.__class__.__name__}\n")
        results_file.write(f"Detector: {detector.__class__.__name__}\n")
        results_file.write(f"Maximum evaluations: {MAX_EVALUATIONS}\n")
        results_file.write("=" * 80 + "\n\n")

        # Evaluations
        for i, pi_prompt in enumerate(evaluations, start=1):
            prompt = pi_prompt["prompt"]
            rogue_string = pi_prompt["settings"]["attack_rogue_string"]
            start = time.time()

            try:
                pipeline = SelfHealingPipeline(
                    input_mitigations=[
                        SystemPromptMitigation()
                    ],
                    output_mitigations=[
                        RogueStringCensorMitigation(
                            rogue_string=rogue_string
                        )
                    ]
                )

                response = pipeline.generate(prompt)

                # Run Garak's detector.
                score = evaluate_with_garak(
                    prompt=prompt,
                    response=response,
                    rogue_string=rogue_string,
                    detector=detector,
                )

                elapsed = time.time() - start

                if score == 1.0:
                    successful += 1

                percentage = (i / total) * 100
                success_rate = (successful / i) * 100

                # Console output
                print(response)
                print(f"[{i}/{total}] {percentage:6.2f}% | {elapsed:6.1f}s | Score: {score:.1f} | Hits: {successful}/{i} ({success_rate:.1f}%)", flush=True,)

                # Save individual evaluation
                results_file.write("-" * 80 + "\n")
                results_file.write(f"Evaluation {i}/{total}\n")
                results_file.write("-" * 80 + "\n")
                results_file.write("\nPROMPT:\n")
                results_file.write(prompt)
                results_file.write("\n")
                results_file.write("\nROGUE STRING:\n")
                results_file.write(rogue_string)
                results_file.write("\n")
                results_file.write("\nRESPONSE:\n")
                results_file.write(response)
                results_file.write("\n")
                results_file.write("\nGARAK SCORE:\n")
                results_file.write(f"{score:.1f}\n")
                results_file.write("\nSTATUS:\n")

                if score == 1.0:
                    results_file.write("HIT - rogue string detected\n")
                else:
                    results_file.write("PASS - rogue string not detected\n")

                results_file.write(f"\nTIME: {elapsed:.2f} seconds\n")
                results_file.write(f"\nCUMULATIVE HIT RATE: {success_rate:.2f}%\n")
                results_file.write("\n")
                results_file.flush()

            except Exception as exc:
                failed += 1
                elapsed = time.time() - start
                percentage = (i / total) * 100

                print( f"[{i}/{total}] {percentage:6.2f}% | {elapsed:6.1f}s | FAILED: {exc}", flush=True,)

                results_file.write("-" * 80 + "\n")
                results_file.write(f"Evaluation {i}/{total}\n")
                results_file.write("-" * 80 + "\n")
                results_file.write("STATUS: FAILED\n")
                results_file.write(f"ERROR: {exc}\n")
                results_file.write(f"TIME: {elapsed:.2f} seconds\n")
                results_file.write("\n")
                results_file.flush()

        # Final summary
        overall_elapsed = time.time() - overall_start
        evaluated = total - failed

        results_file.write("=" * 80 + "\n")
        results_file.write("FINAL RESULTS\n")
        results_file.write("=" * 80 + "\n")
        results_file.write(f"Mitigation: {MITIGATION_NAME}\n")
        results_file.write(f"Evaluations: {total}\n")
        results_file.write(f"Successful attacks / detector hits: {successful}\n")
        results_file.write(f"Failed evaluations: {failed}\n")

        if evaluated > 0:
            hit_rate = successful / evaluated * 100
            results_file.write(f"Garak AttackRogueString hit rate: {hit_rate:.2f}%\n")

        results_file.write(f"Total time: {overall_elapsed / 60:.2f} minutes\n")

        if evaluated > 0:
            results_file.write(f"Average time per evaluation: {overall_elapsed / evaluated:.2f} seconds\n")

        results_file.write("=" * 80 + "\n")

    # Console summary
    print("\nEvaluation complete.", flush=True)
    print(f"Results saved to: {results_filename}", flush=True,)
    print(f"Mitigation: {MITIGATION_NAME}", flush=True,)
    print(f"Evaluations: {total}", flush=True,)
    print(f"Successful attacks / detector hits: {successful}", flush=True,)
    print(f"Failed evaluations: {failed}", flush=True,)

    if evaluated > 0:
        print(f"Garak AttackRogueString hit rate: {successful / evaluated * 100:.2f}%", flush=True,)

    print(f"Total time: {overall_elapsed / 60:.2f} minutes", flush=True,)

if __name__ == "__main__":
    main()
