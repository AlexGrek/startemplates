use crate::validation::*;

pub fn validate_username(username: &str) -> Result<String, String> {
    let uppercase = force_uppercase()(username);
    let validators: Vec<ValidatorFn> = vec![
            limit_length(25),
            allow_only_alphanumerics_and_specials(None),
            not_start_with_digit(),
        ];
    run_validators(&uppercase, &validators)?;
    return Ok(uppercase);
}