# Web Speech: never restart recognition in onend on phones/tablets

**Bit us:** nest_assistant mic, Fuse demo tablet test, 2026-10-31.

The mic used `continuous=false` on Android/iOS and restarted a new `SpeechRecognition` from
`onend` until the user tapped off (to fake continuous dictation). On a tablet that means a
start tone at every pause, a `no-speech` -> `onend` -> restart loop while silent, and a
listener that never ends unless tapped. iPadOS also reports a Mac user agent, so UA sniffing
for "phone" misses iPads entirely.

**Rule:** one tap = one recognition session, `continuous=false` everywhere, no restart.
Listening ends when the speaker stops; tap again to add more. Rebuild the transcript from
ALL `e.results` on every `onresult` (never accumulate across events) so a repeated or revised
result cannot double words, and keep whatever is on screen when it ends (Android does not
always mark the last result final).

Also: a panel that auto-sends what it heard must clear old text on open, or an unsaved
note from last time gets sent as the next question.

Separate trap from the same test: the job card mic opened Ask instead of Note because the
`nest_assistant_note_forms` hook lives in fuse_manufacturing and that app was not updated on
the bench. Check `frappe.boot.nest_assistant.note_forms` in the browser after a deploy.
