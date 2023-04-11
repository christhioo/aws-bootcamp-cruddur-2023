INSERT INTO public.users (display_name, handle, cognito_user_id)
VALUES
  ('Christhio Brown', 'christhio' ,'MOCK'),
  ('Chris Bayko', 'bayko' ,'MOCK'),
  ('Loren Ipsum', 'loren', 'MOCK')
  ;

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'christhio' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )