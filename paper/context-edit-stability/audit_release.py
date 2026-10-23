"""Bind the current local review packet and enumerate remaining publication steps."""
from hashlib import sha256
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / 'paper/context-edit-stability'


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    fields = json.loads((PAPER / 'submission-fields-draft.json').read_text())
    render = json.loads((PAPER / 'render-verification.json').read_text())
    delivery = json.loads((ROOT / 'milestones/M31-delivery-verification.json').read_text())
    companion = ROOT / 'paper/context-edit-stability-companion.zip'
    need(delivery['status'] == 'pass' and sha256(companion.read_bytes()).hexdigest() == delivery['archive_sha256'], 'Untested companion bytes')
    for relative, digest in render['artifact_sha256'].items():
        need(sha256((ROOT / relative).read_bytes()).hexdigest() == digest, f'Changed document artifact: {relative}')
    need(fields['artifact_sha256'] == render['artifact_sha256'], 'Field/document mismatch')
    need(fields['abstract'].isascii() and len(fields['abstract']) == fields['abstract_characters'] <= 1920, 'Abstract format')
    tex = (PAPER / 'main.tex').read_text()
    need('Trần Vũ Bảo Minh' in tex and 'Independent Researcher' in tex, 'User identity not in source')
    need(all(r'\label{'+label+'}' in tex for label in ('thm:reject', 'cor:singleton', 'lem:dominance', 'thm:accepting')), 'Proof scope missing')
    need('Generative AI was used substantially' in tex and 'author\'s substantive review is pending' in tex, 'AI/review status missing')
    need(fields['license'] is None and fields['actual_submission'] == 'absent' and fields['arxiv_identifier'] is None, 'Unapproved external state')
    with zipfile.ZipFile(ROOT / 'paper/context-edit-stability-source.zip') as archive:
        need(archive.namelist() == ['main.tex'] and archive.testzip() is None
             and archive.read('main.tex') == (PAPER / 'main.tex').read_bytes(), 'Minimal source ZIP mismatch')
    full = json.loads((ROOT / 'reproducibility/stability/verification/finite_and_relocated_source.json').read_text())
    need(full['finite_reexecution']['E008_artifacts_reconstructed_byte_identically'] == 4
         and full['finite_reexecution']['E009_formula_cases_recomputed'] == 18779, 'Incomplete finite reproduction')
    need(full['raw_source_verification']['raw_target_decisions_checked'] == 18734
         and full['raw_source_verification']['raw_coordinate_witnesses_checked'] == 26453, 'Incomplete source reconstruction')
    requirements = {
        'scoped_structural_results': 'theorems_and_proofs_present_under_explicit_model_self_review',
        'worldwide_originality': 'not_claimed_targeted_literature_comparison_only',
        'finite_mathematical_evidence': 'pass_reconstructed_E008_and_all_18779_E009_formula_cases',
        'constructed_computation': 'frozen_inputs_witnesses_censoring_and_arithmetic_verified_not_timing_rerun',
        'reused_source_evidence': 'pass_source_pins_original_code_radii_labels_and_26453_witnesses',
        'negative_and_censored_outcomes': 'preserved_zero_rejected_gain_and_two_unresolved_full_models',
        'new_document_and_source_package': 'pass_seven_pages_M30_visual_fonts_and_independent_extracted_source_compile',
        'portable_companion': 'pass_extracted_isolated_normal_optimized_and_relocated_source_checks',
        'author_name_and_affiliation': 'user_supplied_display_preserved_form_ASCII_proposal_unapproved',
        'substantive_owner_content_approval': 'not_given_for_new_draft',
        'generative_AI_disclosure': 'present_author_responsibility_pending_owner_review',
        'independent_peer_review': 'not_required_for_preparation_not_claimed_as_obtained',
        'license': 'unselected_owner_decision_required',
        'arxiv_account': 'no_authenticated_account_evidence_user_previously_reported_none',
        'endorsement': 'unknown_requires_actual_account_flow',
        'category': 'cs.DB_technical_candidate_not_moderator_confirmed',
        'metadata_form_rendering': 'not_tested_live',
        'arxiv_server_compile_and_PDF_check': 'not_run_local_XeLaTeX_only',
        'remove_draft_and_pending_review_markers': 'after_owner_approval_then_recompile_repackage_and_reverify',
        'actual_submission': 'absent',
        'public_arxiv_record': 'absent',
    }
    readiness = dict(date='2026-10-23', status='prepared_for_owner_review_not_submission_complete',
                     goal_complete=False, completion_proven=False, requirements=requirements,
                     previous_goal_turn='progress_E011_source_study_and_M30_structural_preprint',
                     current_turn='progress_M31_portable_companion_full_reproduction_and_claim_audit',
                     owner_review_dependency_first_concrete_new_packet_turn=True,
                     independent_peer_review_is_submission_gate=False,
                     license_selected=False, publication_authorized_for_this_draft=False,
                     artifacts={**render['artifact_sha256'],
                                'paper/context-edit-stability-companion.zip': delivery['archive_sha256']},
                     companion_members=delivery['archive_members'], claims_mapped=8,
                     abstract_characters=fields['abstract_characters'],
                     remaining_owner_decisions=['substantive_review_of_exact_new_draft', 'author_form_rendering_choice', 'license'],
                     remaining_external_steps=['account_and_endorsement_state', 'server_compile_and_metadata_review', 'submission_and_public_record_verification'],
                     official_guidance_checked='2026-10-23',
                     official_sources=['https://info.arxiv.org/help/submit/index.html',
                                       'https://info.arxiv.org/help/prep.html',
                                       'https://info.arxiv.org/help/faq/texlive.html',
                                       'https://info.arxiv.org/help/moderation/index.html',
                                       'https://info.arxiv.org/help/license/index.html',
                                       'https://info.arxiv.org/help/endorsement.html',
                                       'https://arxiv.org/category_taxonomy'])
    (PAPER / 'submission-readiness.json').write_text(json.dumps(readiness, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status=readiness['status'], goal_complete=False, companion_members=delivery['archive_members'],
                          claims_mapped=8, abstract_characters=fields['abstract_characters'], actual_submission='absent'), indent=2))


if __name__ == '__main__':
    main()
