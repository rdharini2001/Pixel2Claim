# Criteria for Claims and Falsification

Draft 1, 18 November 2026.

## 1. Problem

CT scans carry header fields that other systems rely on, such as body part, contrast use and modality. These fields are often wrong or missing. One study found the body part tag wrong in 15.3% of routine images [1]. Another, on head, neck and chest CT scans, found the contrast tag is missing or wrong in 75.6% of scans [3].

Models that read body part and contrast directly from the image already exist and work well. FALCON scored an F1 of 98.1 to 99.4% for contrast and 100% for body part on 1,348 external scans [2]. What is missing is a way to decide, for each header field, whether to keep the tag, replace it with the image's answer, or send the scan for a human review. That decision should come with a reason that can be checked.

## 2. Our approach

We use an existing image model and add a decision layer on top. For each field, the layer gives one of three answers: accept the tag, override it, or escalate for human review. Each answer comes with a record of the evidence behind it. A short text explanation is written from that record and a checker confirms that every sentence matches the record. Free-text header fields are treated as data and never as instructions.

## 3. Related work

Other work already checks headers against images. It covers study type [4], body region [5], and body part and contrast quality checks [6]. A recent MRI paper flags corrupted metadata by comparing image and metadata embeddings, with an AUC up to 0.997 for large missing-tag errors [7]. It does not report a guaranteed error rate and does not correct tags automatically.

We found no earlier work that combines a guaranteed error rate, checked explanations and protection against planted text. 

## 4. Claims

Two terms are used below. The error rate is the share of accepted tags that are wrong. Coverage is the share of scans where the tag is accepted.

1. **Controlled error rate.** A cutoff is set on the image score, using a separate set of scans, so that the error rate among accepted tags stays at or below a target such as 5%. This method is called conformal calibration. The target holds on scans from a collection we did not use for calibration.

2. **Better than simple baselines.** At the same error rate, our method accepts more tags than (a) trusting every tag and (b) a fixed confidence cutoff on the image model.

3. **Checkable explanations.** Every sentence of an explanation matches the evidence record. Removing the evidence it cites changes the decision.

4. **Resistance to planted text.** Text in free-text header fields cannot change a decision. We test this with attacks written to fool the system.

The guarantee in claim 1 assumes that the calibration scans look like the test scans. Our two sets come from different collections, so this may not hold. We will report any gap between the target and the result.

## 5. Criteria to test each Claim

Numbers marked "first guess" are fixed after a small pilot run and before the main test. They are not changed afterward.

| Claim | Supported if | Dropped if |
|---|---|---|
| 1 | On the held-out collection, the error rate is at most 5% plus the 95% margin of error, and coverage is at least 80% (first guess) | The error rate is above the target by more than the margin of error, or coverage is below 50% |
| 2 | Coverage is higher than both baselines at the same error rate, and the 95% intervals do not overlap | The confidence-cutoff baseline matches our method within the intervals |
| 3 | The checker rejects every planted false sentence, and removing the cited evidence changes the decision in at least 90% of override cases (first guess) | Removing the cited evidence changes the decision no more often than removing random evidence |
| 4 | Attack success is at most 1% (first guess) | Any attack we write succeeds more than 5% of the time |

For claim 4, an earlier small test with language-model agents (22 studies, one run) found that they followed planted instructions in 46 to 92% of cases. We use it as a rough reference, not as a controlled baseline.

## 6. When we drop a claim

If a fixed confidence cutoff on the image model does as well as our method, claim 2 is dropped. The contribution then rests on claims 3 and 4, and we say so.

If the image model is not accurate on the held-out collection, we stop and fix that first.

## References

[1] M. O. Güld et al. Quality of DICOM header information for image categorization. Proc. SPIE 4685, 2002.
[2] FALCON: open-access fully automated intravenous contrast detection and body part classification for CT scans. doi:10.1007/s10278-026-01865-8
[3] Z. Ye et al. Deep learning-based detection of intravenous contrast in computed tomography scans. arXiv:2110.08424.
[4] F. Jonske et al. MOMO: Deep learning-driven classification of external DICOM studies for PACS archiving. European Radiology 32, 2022. doi:10.1007/s00330-022-08926-w
[5] P. Raffy et al. Deep learning body region classification of MRI and CT examinations. arXiv:2104.13826.
[6] ImageQC-net: deep learning image quality control for CT body part and contrast enhancement. BMC Medical Imaging, 2022. doi:10.1186/s12880-022-00815-4
[7] Metadata supervised imaging representations for modelling and controlling acquisition variability. arXiv:2607.11295.
