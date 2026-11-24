# Music: Politician

## Input
File in `input/`, what it is (played melody, hummed, MIDI).

## Analysis
- Key / mode:
- Tempo (BPM) and meter:
- Range and contour:
- Phrase lengths:
- Intervals and motifs worth keeping:

## Role in the film
Where music enters, where it must stay silent, what it does to the scene (never decoration).

## Direction
- Genre and era:
- Instrumentation (who plays on screen in the Seedance shot):
- Mood, dynamics, density:

## Cues
| Cue | Picture range | Length | Prompt file | Best take | Notes |
|---|---|---|---|---|---|
| music_spy-synth_T01 | test, no picture range yet | 30 s | prompts/music_spy-synth_T01.txt | not rated | Seedance 2.5, 480p 16:9, 90 credits, job 20002f97-fe79-48da-ba3f-f295343351f2, Higgsfield MUSIC. D minor 100 BPM asked. Audio 32 kHz. |
| music_80s-action-synth_T01 | test, no picture range yet | 30 s | prompts/music_80s-action-synth_T01.txt | not rated | Seedance 2.5, 480p 16:9, 90 credits, job fd82ec8d-59c5-4a46-ab26-391932b1ca79, Higgsfield MUSIC. Early 80s analog synth action build, E minor 120 BPM asked. Audio 32 kHz. |
| music_80s-action-synth_T02 | test, no picture range yet | 30 s | prompts/music_80s-action-synth_T02.txt | not rated | Seedance 2.5, 480p 16:9, 90 credits, job 8be937bb-8818-4c09-a805-dcdbb0ed0230, Higgsfield MUSIC. T01 made darker and slower: 80 BPM, sparse primitive drum machine, no hi-hats. Audio 32 kHz. |
| music_80s-action-synth_T02_end_raw | extension only | 5 s | prompts/music_80s-action-synth_T02_end.txt | - | Seedance 2.5 video_extension forward of T02, 480p, 15 credits, job 6882b897-8141-4bed-957f-3dd437e41710, Higgsfield MUSIC. |
| music_80s-action-synth_T02_end | complete clip, no picture range yet | 35 s | prompts/music_80s-action-synth_T02_end.txt | 5 (Leonard: "perfect" on T02) | edit: T02 frames 0-719 + T02_end_raw joined in ffmpeg. Ending starts at 30.00 s; level drops from about 32.5 s to -39 dB at 34.5 s. Audio 32 kHz. |
| music_80s-action-synth_T03_raw | extension only | 30 s | prompts/music_80s-action-synth_T03.txt | - | Seedance 2.5 video_extension forward of T02 cut to 0-11.00 s (_local/music_80s-action-synth_T02_head11.mp4, media 05b41f32-a4c7-4688-bb05-070bf8bd8762), 480p, audio on, 90 credits, job c04cd9d7-8507-408c-991a-52f1c4ed9534, Higgsfield MUSIC. Audio 32 kHz. |
| music_80s-action-synth_T03 | complete clip, no picture range yet | 41 s | prompts/music_80s-action-synth_T03.txt | 1 (inferred: Leonard "what the hell is that?": yell only, no drums, guitars or power) | edit: T02 frames 0-263 (0-11.00 s) + T03_raw end to end, no crossfade. Extension starts at 11.00 s (T02 measured 80 BPM, beat at 10.98 s; [ASSUMPTION] Leonard's "10s:20" = 10.83 s). Mean level T02 -21.0 dB, extension -22.3 dB: no loudness jump at the hit. |
| music_80s-action-synth_T04_eleven | power section, no picture range yet | 36 s | prompts/music_80s-action-synth_T04_eleven.txt | not rated | ElevenLabs Music v2.5, vocals allowed, 5.24 credits, job 8acc7766-17b1-4256-b908-051cbdbe59cc, Higgsfield MUSIC. 80 BPM, E root. No synth lead-in: the band plays from 0 s; strongest onset 2.97 s. mp3 44.1 kHz + wav. Check ElevenLabs rights terms before locking into the edit. |
| music_80s-action-synth_T04_eleven_join | complete clip, no picture range yet | 44.1 s | T02 + T04_eleven prompts | not rated | edit: T02_end audio 0-11.00 s (10 ms fade) + T04_eleven from 2.96 s, no crossfade. Hit at 11.00 s. wav 44.1 kHz + mp3. |
| music_80s-action-synth_T05_eleven | power section, no picture range yet | 48 s | prompts/music_80s-action-synth_T05_eleven.txt | 1 (inferred: Leonard "what the fuck is that": other notes and chords than T02, metal rhythm, too long) | ElevenLabs Music v2.5, 42 s asked, 48 s delivered, vocals allowed, 6.11 credits, job 2fe9fa9f-8939-4809-ab77-ef50f2997022, Higgsfield MUSIC. 80 BPM, beats at 0.73 + 0.75k s. Drum intro 0-6 s, band in about 6.5 s, full level to about 43 s, stop decays 43-44.5 s. mp3 44.1 kHz + wav. Check ElevenLabs rights terms before locking into the edit. |
| music_80s-action-synth_T05_eleven_join | complete clip, no picture range yet | 59 s | T02 + T05_eleven prompts | 1 (inferred, as T05_eleven) | edit: T02_end audio 0-11.00 s (20 ms fade) + T05_eleven whole, no crossfade. Drum intro at 11.00 s, band in about 17.5 s, ending about 54-55.5 s. wav 44.1 kHz + mp3. |
| music_80s-action-synth_T06_eleven | power section, no picture range yet | 32 s | prompts/music_80s-action-synth_T06_eleven.txt | 1 (inferred: Leonard "flat and lobotomized") | ElevenLabs Music v2.5, vocals allowed, 4.66 credits, job 39bf69cc-9380-4a65-9a62-0671d849fda2, Higgsfield MUSIC. 80 BPM, beats at 0.35 + 0.75k s. No solo drum intro (full level from 0 s). Bass leaves E at 4-12 s (D, C#, A#). Stop about 29 s. mp3 44.1 kHz + wav. Check ElevenLabs rights terms before locking into the edit. |
| music_80s-action-synth_T06_eleven_join | complete clip, no picture range yet | 42.7 s | T02 + T06_eleven prompts | 1 (inferred, as T06_eleven) | edit: T02_end audio 0-11.00 s (20 ms fade) + T06_eleven from 0.35 s (on the beat), no crossfade. Stop about 39.6 s. wav 44.1 kHz + mp3. |
| music_80s-action-synth_T07_eleven | power section, no picture range yet | 33 s | prompts/music_80s-action-synth_T07_eleven.txt | 2 (inferred: "nothing like" the references; guitar build "not bad but not great") | ElevenLabs Music v2.5, vocals allowed, 4.80 credits, job 13242416-7440-4204-8ac0-97a41390fa5a, Higgsfield MUSIC. Build from -70 dB to -25 dB over 0-11.5 s, explosion 11.97 s, bass on E throughout, 80 BPM, beats at 0.72 + 0.75k s, stop about 30.3 s. mp3 44.1 kHz + wav. Check ElevenLabs rights terms before locking into the edit. |
| music_80s-action-synth_T07_eleven_join | complete clip, no picture range yet | 44.1 s | T02 + T07_eleven prompts | 2 (inferred, as T07_eleven) | edit (mix): T02_end 0-22.98 s, fade out 17-22.98 s, plus T07_eleven delayed 11.01 s; explosion at 22.98 s on T02's beat; stop about 41.3 s. wav 44.1 kHz + mp3. |
| music_80s-action-synth_T08_eleven | power section, no picture range yet | 32 s | prompts/music_80s-action-synth_T08_eleven.txt | 1 (inferred: "horrendously cringe") | ElevenLabs Music v2.5, vocals allowed, 4.66 credits, job 86ec6149-d500-41e1-b6dc-0e6b9223a28c, Higgsfield MUSIC. Full level from 0 s (no drum build), level pattern repeats every 6 s, bass on D#/D/C not E, 80 BPM, stop about 30.5 s. Not joined. mp3 44.1 kHz + wav. |
| music_80s-action-synth_T09_eleven_drums | part 1 of 3 | 9 s | prompts/music_80s-action-synth_T09_eleven_drums.txt | 1 (inferred: "obscene ... stupid as fuck") | ElevenLabs Music v2.5, instrumental, 7 s asked, 1.02 credits, job db8e8c40-27cd-449e-9ef8-6206836a70ed. Groove, build, final hit at 6.02 s, decay. |
| music_80s-action-synth_T09_eleven_body | part 2 of 3 | 24 s | prompts/music_80s-action-synth_T09_eleven_body.txt | 1 (inferred: "obscene ... stupid as fuck") | ElevenLabs Music v2.5, vocals allowed, 3.49 credits, job 4980fe5e-41cb-4031-ad92-1765fccb14c9. 0.7 s silence, first hit 0.74 s, 80 BPM, beats 0.74 + 0.75k s, bass mostly E. |
| music_80s-action-synth_T09_eleven_chord | part 3 of 3 | 8 s | prompts/music_80s-action-synth_T09_eleven_chord.txt | 1 (inferred: "obscene ... stupid as fuck") | ElevenLabs Music v2.5, instrumental, 1.17 credits, job 8c93b7ec-47be-4753-a91b-a61204c8e19c. E-B power chord, attack 0.03 s, decays to silence by 7.8 s. |
| music_80s-action-synth_T09_eleven_join | complete clip, no picture range yet | 40 s | T02 + T09_eleven part prompts | 1 (inferred: "obscene ... stupid as fuck") | edit (mix): T02_end 0-10.98 s; drums from 4.96 s; body from 10.24 s, cut at 31.98 s; chord + drums' final hit at 31.98 s; limiter -1 dB. Explosion 10.98 s, slam 31.98 s. wav 44.1 kHz + mp3. |
| music_80s-action-synth_T10_eleven_body_v1 | band section, version 1 of 4 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, batch 4, 3.49 credits, job 96250963-40c1-4f1c-9a17-12377b909a89, Higgsfield MUSIC. 80 BPM. Bass: E, drifts to C, A#, C# from 8 s. |
| music_80s-action-synth_T10_eleven_body_v2 | band section, version 2 of 4 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, batch 4, 3.49 credits, job 5728c425-9324-435f-99fe-1fe08578f364, Higgsfield MUSIC. 80 BPM. Bass: E to 16 s, then F#, A#, G#. |
| music_80s-action-synth_T10_eleven_body_v3 | band section, version 3 of 4 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, batch 4, 3.49 credits, job 745071cb-1893-4835-82db-7b55ab643163, Higgsfield MUSIC. 80 BPM. Bass: E throughout, F and F# present. |
| music_80s-action-synth_T10_eleven_body_v4 | band section, version 4 of 4 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, batch 4, 3.49 credits, job a9604eba-5efd-4c5a-85b2-de70fb5b58de, Higgsfield MUSIC. 80 BPM. Bass: G# and E. |
| music_80s-action-synth_T10_eleven_body_v5 | band section, version 5 of 12 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, 3.49 credits, job 8d78cf30-5ca6-4d24-b211-279788e5a253, Higgsfield MUSIC. Bass: A first, then E. |
| music_80s-action-synth_T10_eleven_body_v6 | band section, version 6 of 12 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, 3.49 credits, job 5fb7dcdd-ddb1-4f08-ab1c-20b478bb104d, Higgsfield MUSIC. Bass: D# first, then E. |
| music_80s-action-synth_T10_eleven_body_v7 | band section, version 7 of 12 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, 3.49 credits, job 780c7a59-70d7-4fed-bc18-4c1af4ddf6e9, Higgsfield MUSIC. Bass: E throughout, strongest E (0.78). |
| music_80s-action-synth_T10_eleven_body_v8 | band section, version 8 of 12 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, 3.49 credits, job f6de978c-4b17-424f-af3d-0adbb9afb03b, Higgsfield MUSIC. Bass: E, then G from 12 s. |
| music_80s-action-synth_T10_eleven_body_v9 | band section, version 9 of 12 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, 3.49 credits, job bb8c5db5-a20c-4874-9f11-af426b992957, Higgsfield MUSIC. Bass: between E and F. |
| music_80s-action-synth_T10_eleven_body_v10 | band section, version 10 of 12 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, 3.49 credits, job 80ee90cf-ddab-4e7a-800e-b0da0f058399, Higgsfield MUSIC. Bass: E, drifts from 12 s. |
| music_80s-action-synth_T10_eleven_body_v11 | band section, version 11 of 12 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, 3.49 credits, job 1bbbc398-c461-47ed-b991-329ac2bd1a3d, Higgsfield MUSIC. Bass: E throughout (0.48). |
| music_80s-action-synth_T10_eleven_body_v12 | band section, version 12 of 12 | 24 s | prompts/music_80s-action-synth_T10_eleven_body.txt | not rated | ElevenLabs Music v2.5, 3.49 credits, job 98c35f24-55f6-4886-a69b-73ca4006eeeb, Higgsfield MUSIC. Bass: E throughout (0.38). |
| music_80s-action-synth_T11_comp | complete clip, no picture range yet | 40 s | T02 + T09 drums/chord + T10 body prompts | 1 (inferred: "not how you edit music ... cut as lego") | comp (0 credits): T02_end 0-10.98 s; T09 drums from 4.96 s; T10 v5 0-6.03 s at 10.95 s; v9 9.03-18.03 s at 16.98 s; v7 18.03-24.03 s at 25.98 s; v10 low-passed bass 150 Hz under 10.98-22.98 s; T09 chord + final drum hit at 31.98 s; limiter -1 dB. Leonard's selection notes on T10 v5, v7, v9, v10. |
| music_80s-action-synth_T12_v9edit | complete clip, no picture range yet | 37 s | T02 + T09 drums/chord + T10 body prompt | 1 (inferred: "a whole mess that needs heavy redoing") | edit (0 credits), one recording: T02_end 0-10.98 s; T09 drum build (no final hit) from 4.96 s; T10 v9 whole from 7.95 s, its first hit at 10.98 s, 6 bars uncut, cut before its ending at 28.97 s; T09 chord at 28.98 s; limiter -1 dB. No level jump at 10.98 s. |
| music_80s-action-synth_T13_remix | complete clip, no picture range yet | 37 s | T02 + T09 drums/chord + T10 body prompt | 2 (inferred: transitions still sound cut, out of rhythm) | remix (0 credits, 07-music/remix_T13.py): T02 dips 5 dB under a rising drum build; hit 10.98 s; T10 v5 bars 1-2, v9 9.03-15.03 s, v7 last 2 bars, EQ- and level-matched, eighth-note equal-power crossfades into each downbeat; v10 bass (low-pass 140 Hz) under 10.98-22.98 s; chord 28.98 s; bus compressor 3:1, limiter -1 dB. |
| music_80s-action-synth_T14_eleven_v1 | full cue, version 1 of 4 | 33 s | prompts/music_80s-action-synth_T14_eleven.txt | not rated | ElevenLabs Music v2.5, batch 4, 4.80 credits, job b9f7f88b-0eff-40ca-8ccb-044d544d3672, Higgsfield MUSIC. off E, 3 s repeating pattern, long fade from 24 s. |
| music_80s-action-synth_T14_eleven_v2 | full cue, version 2 of 4 | 33 s | prompts/music_80s-action-synth_T14_eleven.txt | not rated | ElevenLabs Music v2.5, batch 4, 4.80 credits, job ba6ebf65-c6f7-435e-b1c2-d8686a4b5a4f, Higgsfield MUSIC. off E, rigid 1.5 s pattern, stop at 27 s. |
| music_80s-action-synth_T14_eleven_v3 | full cue, version 3 of 4 | 33 s | prompts/music_80s-action-synth_T14_eleven.txt | not rated | ElevenLabs Music v2.5, batch 4, 4.80 credits, job 1dc2f7f5-3561-4627-aa8e-6f82abcc1d88, Higgsfield MUSIC. on E, quieter 0-6 s, hit 6.01 s, dead stop 30.3 s. |
| music_80s-action-synth_T14_eleven_v4 | full cue, version 4 of 4 | 33 s | prompts/music_80s-action-synth_T14_eleven.txt | not rated | ElevenLabs Music v2.5, batch 4, 4.80 credits, job 69fe05b9-fbe6-4802-b0d5-a3972314342f, Higgsfield MUSIC. mostly off E, hit 10.39 s. |
| music_80s-action-synth_T14_eleven_v3_join | complete clip, no picture range yet | 38 s | T02 + T14 prompt | 4 (inferred: "almost there") | edit (one join): T02_end 0-11.00 s dipping 7 dB from 5 s; T14 v3 from 4.99 s, its hit on T02's beat at 11.00 s; limiter -1 dB. |
| music_80s-action-synth_T14_eleven_v3_mix2 | complete clip, no picture range yet | 43 s | T02 + T14 prompt + T09 chord prompt | 2 (inferred: "actually worse"; drums start too loud and abrupt) | edit (0 credits): T02 fades over 10.90-11.75 s under the hit; T14 v3 from 4.99 s, hit 11.00 s, end faded 35.29-35.43 s; T09 chord on v3's last downbeat at 35.01 s; glue compressor 2:1, limiter -1 dB, -13.9 LUFS. |
| music_80s-action-synth_T14_eleven_v3_join_v2 | complete clip, no picture range yet | 38 s | T02 + T14 prompt | 4 (inferred: "this is good") | edit (0 credits): v3_join with one change: v3's first 6 s fade in on a square-law curve from silence to full at the hit (11.00 s). |
| music_80s-action-synth_T14_eleven_v3_join_v3 | complete clip, no picture range yet | 35 s | T02 + T14 prompt | not rated | edit (0 credits): join_v2 minus one bar of v3 (its 18.01-21.01 s, most similar to its neighbours), 15 ms crossfade before the downbeat at 23.02 s. Hit 11.00 s, end stop about 32.4 s. |
| music_80s-action-synth_T14_eleven_v3_join_v4 | complete clip, no picture range yet | 30 s | T02 + T14 prompt | 3 (inferred: fade-out "stupid", otherwise kept) | edit (0 credits): join_v3 minus v3's bar 7 (24.01-27.01 s), last bar fades (quarter-sine) 26.0-29.4 s to silence, treble -2 dB at 6 kHz, limiter -1 dB. Hit 11.00 s. |
| music_80s-action-synth_T14_eleven_v3_join_v5 | complete clip, no picture range yet | 29 s | T02 + T14 prompt | 2 (inferred: "you messed up the editing"; started on a chopped note) | edit (0 credits): join_v4 with T02 starting at its 3.00 s (one bar off the start, hit at 8.00 s) and no fade-out (v3's own stop at about 26.4 s); treble -2 dB at 6 kHz, limiter -1 dB. |
| music_80s-action-synth_T14_eleven_v3_join_v6 | complete clip, no picture range yet | 29 s | T02 + T14 prompt | not rated | edit (0 credits): join_v5 with the start fixed: T02 0-0.52 s (its own lead-in) spliced to T02 from 3.51 s on the beat, 10 ms crossfade. Hit 8.02 s, v3's own stop at about 26.4 s, treble -2 dB, limiter -1 dB. |
| music_80s-tension-strings_T01 | test, no picture range yet | 30 s | prompts/music_80s-tension-strings_T01.txt | not rated | Seedance 2.5, 480p 16:9, 90 credits, job b20b1738-c2a0-43d7-b8d5-a890fec2d835, Higgsfield MUSIC. Early 80s synth-string tension underscore, E minor 60 BPM asked, no drums. Audio 32 kHz. |
| music_80s-tension-strings_T02 | blocked | 30 s | prompts/music_80s-tension-strings_T02.txt | - | Seedance 2.5, 480p 16:9, job 238c0c52-7ae1-470f-a046-b05e64e1b02c blocked by the output filter (status nsfw), 90 credits refunded 13:24 UTC. No file. |
| music_80s-tension-strings_T02 | test, no picture range yet | 30 s | prompts/music_80s-tension-strings_T02.txt | not rated | Resubmit of the blocked job, prompt unchanged: passed. Seedance 2.5, 480p 16:9, 90 credits, job a8569973-9aab-4740-bc81-cafc993a8dd4, Higgsfield MUSIC. Orchestral strings + synth bass pulse, E minor 60 BPM. Audio 32 kHz. |
| music_80s-tension-strings_T03 | blocked | 30 s | prompts/music_80s-tension-strings_T03.txt | - | Seedance 2.5, 480p 16:9, job 75622f09-cee1-49e4-a969-1e7910cb7b55 blocked by the output filter (status nsfw), 90 credits refunded 13:55 UTC. No file. |
| music_80s-tension-strings_T04 | blocked | 30 s | prompts/music_80s-tension-strings_T04.txt | - | Seedance 2.5, 480p 16:9, job f87c2817-1488-4c26-abcc-67fc0cbbee17 (folder MUSIC) blocked by the output filter (status nsfw), 90 credits refunded 14:10 UTC. No file. Synth-only picture did not avoid the block. |
| music_80s-tension-strings_T05_eleven | test, no picture range yet | 30 s | prompts/music_80s-tension-strings_T05_eleven.txt | not rated | ElevenLabs Music v2.5 on Higgsfield, instrumental, 4.36 credits, job 671133be-70db-4c24-bc02-c0d14e25e0ea, Higgsfield MUSIC. T04 music text without the picture. mp3 128 kbps 44.1 kHz + wav. Check ElevenLabs rights terms before locking into the edit. |
| music_90s-crescendo_T01_eleven | test, no picture range yet | 45 s | prompts/music_90s-crescendo_T01_eleven.txt | 1 (inferred: Leonard "repulsive") | ElevenLabs Music v2.5, instrumental, 6.54 credits, job eab674b7-867e-4b57-bfed-227696328ad1, Higgsfield MUSIC. Hybrid orchestra + synth crescendo, E minor 100 BPM asked. mp3 44.1 kHz + wav. Mean level only -19.3 dB at 2 s to -18.1 dB at 32 s: the build is not in loudness (density not measured). |
| music_90s-crescendo_T02 | part 1 of 2, no picture range yet | 30 s | prompts/music_90s-crescendo_T02.txt | 1 (inferred: Leonard "horrific"); extension 011b dropped | Seedance 2.5, 480p 16:9, 90 credits, job 82a03900-8a9b-4c63-90b9-586863e0b2f8, Higgsfield MUSIC. Hybrid orchestra + synth crescendo, E minor 100 BPM asked. Mean level -26.6 dB at 2 s rising to -20.4 dB at 29 s. Audio 32 kHz. |
| music_late80s-synth-underscore_T01 | test, no picture range yet | 30 s | prompts/music_late80s-synth-underscore_T01.txt | not rated | Seedance 2.5, 480p 16:9, 90 credits, job 58266983-ea92-4ae4-932e-216d45550d1a, Higgsfield MUSIC. Late 1980s digital synth underscore (sampler, FM, mallet ostinato, synth pan flute), E minor 96 BPM asked. Audio 32 kHz. |
| music_political-thriller_T01 | test, no picture range yet | 30 s | prompts/music_political-thriller_T01.txt | not rated | Seedance 2.5, 480p 16:9, 90 credits, job aa329c5e-24d2-4846-94d2-8e9360c287c7, Higgsfield MUSIC. Fresh start: late 80s to 90s orchestral political thriller underscore over synth bed and muted electronic loop, D minor 92 BPM asked. Audio 32 kHz. |
| music_political-thriller_T02 | test, no picture range yet | 30 s | prompts/music_political-thriller_T02.txt | 1 (inferred: Leonard "horrendous, sounds like default background music") | Seedance 2.5, 480p 16:9, 90 credits, job 0a206bb2-e059-4b62-95f8-a97f3e0ed6b4, Higgsfield MUSIC. T01 without rhythm: held chords, no ostinato, no percussion, no tempo. Audio 32 kHz. |
| music_political-thriller_T03 | blocked | 30 s | prompts/music_political-thriller_T03.txt | - | Seedance 2.5, 480p 16:9, job dacdfcd1-8e15-4a49-9826-3a9b390df250 (folder MUSIC) blocked by the output filter (status nsfw), 90 credits refunded 16:02 UTC. No file. |
| music_political-thriller_T03 | test, no picture range yet | 30 s | prompts/music_political-thriller_T03.txt | not rated | Resubmit of the blocked job, prompt unchanged: passed. Seedance 2.5, 480p 16:9, 90 credits, job b8e780e9-65ed-4f44-a34f-a1f299fe4287, Higgsfield MUSIC. Composed: D minor 80 BPM, strings and two horns. Audio 32 kHz. |
| music_7min-style_T01 | test, no picture range yet | 30 s | prompts/music_7min-style_T01.txt | not rated | Seedance 2.5, 480p 16:9, 90 credits, job d1dae924-69e2-4778-9a03-2c2f1b9ccbcc, Higgsfield MUSIC. Built on the 7 Minutes reference analysis. Level -37 dB 0-11 s, rises to -24 dB at 18 s, holds to 26 s, then drops to -44 dB at 28.5 s: the planned loudest point at 24-30 s did not happen. Audio 32 kHz. |
| music_clancy-loop_T01 | test, no picture range yet | 30 s | prompts/music_clancy-loop_T01.txt | not rated | Seedance 2.5, 480p 16:9, 90 credits, job 515721f5-4d4a-4bae-8ced-cb92f7c5c59f, Higgsfield MUSIC. Orchestral military version of the 7 Minutes 3:22 loop (B-flat minor, F#, G, C#), 80 BPM asked. Level -39 dB at the start, pulsing every 3 s (-29 / -35 dB), rising to -19 dB at 27 s. Audio 32 kHz. |
| music_clancy-loop_T01_eleven | test, no picture range yet | 30 s | prompts/music_clancy-loop_T01_eleven.txt | 1 (inferred: Leonard "absolute crap") | ElevenLabs Music v2.5, instrumental, 4.36 credits, job c0f2eeaa-8680-49f8-b8ff-c01dabfab778, Higgsfield MUSIC. No-repetition version: 10 different chords, ends on G# major. Level -34 dB 0-11 s, jumps to -19 dB at 12 s, then rises slowly to -17 dB at 28.5 s. mp3 44.1 kHz + wav. |
| music_hybrid-thriller_T01 | test, no picture range yet | 30 s | prompts/music_hybrid-thriller_T01.txt | 2 (inferred: Leonard "this is what happens when you give no notes" = too vague) | Seedance 2.5, 480p 16:9, 90 credits, job f5e8db80-01bc-4464-bfff-c52e4452355c, Higgsfield MUSIC. Through-composed hybrid (orchestra + electronics) from the 7 Minutes first-part analysis. Level per 3 s: -30, -40, -42, -31, -34, -38, -33, -32, -17, -18, -26 dB: the drop at 13-18 s and the climax at 24-27 s are there. Audio 32 kHz. |
| music_hybrid-thriller_T02 | test, no picture range yet | 30 s | prompts/music_hybrid-thriller_T02.txt | not rated | Seedance 2.5, 480p 16:9, 90 credits, job 16ce2ae4-bdc2-4646-81b8-08961bb9d49a, Higgsfield MUSIC. Full bar-by-bar score. Measured bass per half bar: C# (bars 1-2), E (3), A/E (4), E (5-6), G/C# (7), G/A (8), G/E (9), B/E (10); score asked G#-G-F#-F-E-D#-D-C#. The C# centre and the final cut (-46 dB at 28.5 s) came through; the falling bass line did not. Audio 32 kHz. |
| music_hybrid-thriller_T03 | test, no picture range yet | 30 s | prompts/music_hybrid-thriller_T03.txt | 1 (inferred: Leonard "what is this, how did we go from the references to THIS") | Seedance 2.5 omni_reference, 480p 16:9, 90 credits, job 6800c145-8044-44d8-a5a0-469a7068daca, Higgsfield MUSIC. @audio1 = input/music_hybrid-thriller_T02_sketch (MIDI render of the T02 score, media b7590404). Measured bass per half bar: G#/G, G#-G, F#, F-E, D# (drop), E, D#, D-C#, C#: follows the score except the drop bars 5-6. Chroma correlation with the sketch 0.87 (T02 without reference: -0.01). Waveform correlation 0.05: not a copy of the sketch audio. Timbre not measurable: needs listening. Audio 32 kHz. |
| music_groove-build_T01 | test, no picture range yet | 30 s | prompts/music_groove-build_T01.txt | 1 (inferred: Leonard "this sucks") | Seedance 2.5 omni_reference, 480p 16:9, 90 credits, job 1bf33a9b-587f-4b43-9a9e-b8706a89d1fb, Higgsfield MUSIC. @audio1 = input/music_groove-build_T01_sketch (media 628f8633), original groove modelled on 7 Minutes 0:34-1:06 (Leonard picked 0:43, drums and build). Level per 3 s matches the sketch (-33, -29, -23, -18, then -17 to -18, -15 at 27 s) but drops to -40 dB at 28.5 s where the sketch has the final hit (-14 dB). Chroma correlation with the sketch 0.36. Audio 32 kHz. |
| music_90s-orchestral-tension_T01 | S04 SH010-SH060 (walk to the impact, 19 s) | 30 s | prompts/music_90s-orchestral-tension_T01.txt | not rated | Seedance 2.5 omni_reference, 480p 16:9, 90 credits, job 6a034aea-a9ef-440c-be19-49e0089e4dab, Higgsfield MUSIC. @audio1 = input/music_90s-orchestral-tension_T01_sketch (MIDI render, media 362a2def); score in music_90s-orchestral-tension_T01.md. C minor 80 BPM. Level per 3 s: -27, -27, -21, -22, -21, -21, -19, -22, -19, -19 dB. Measured bass per bar: C, G, Ab, Ab, G, C, Eb, Eb, Eb, Eb; score asked C pedal bars 1-8, G bars 9-10. Bars 1-2 follow the sketch (C/G/Eb); D-flat (bars 5-6) and B (bars 7-8) not found; bars 7-10 sit on E-flat major instead of Cm(maj7) and G. Chroma correlation with the sketch 0.49. Audio 32 kHz. |

## Composition plan: music_political-thriller_T03 (Leonard 2026-11-23: orchestra only, no synth, no sfx, exact notes, political thriller not soap opera)

D minor, 4/4, 80 BPM: one bar = 240 / 80 = 3 s, 30 s = 10 bars exactly. Orchestra only: strings and two horns. No percussion, no synth, no piano, no choir. Dynamics pp to mp, never louder. Ends unresolved on the dominant.

| Bars | Time | Notes and instruments | Harmony |
|---|---|---|---|
| 1-2 | 0-6 s | Basses and cellos hold low D (D2) pp; violas add A3 on bar 2 | open fifth D-A, no third: cold |
| 3-4 | 6-12 s | Second violins: half notes F4 down to E4, twice (a minor second sigh) | D minor revealed |
| 5-6 | 12-18 s | Two horns in unison: D3 half note, F3 quarter, E3 quarter, then A2 whole note; basses move D2 to B-flat1 on bar 6 | D minor to B-flat major |
| 7-8 | 18-24 s | First violins: high A5 tremolo sul ponticello pp; basses step B-flat1 to A1; violas C-sharp4 | A major (dominant): tension |
| 9-10 | 24-30 s | Horns repeat the motif a step higher: E3 half, G3 quarter, F3 quarter, then hold E3; violin tremolo A5 continues | stays on A, never resolves to D |

Why it should read political thriller, not soap opera: no melody that sings, no warm major resolution, no swells; the only melodic idea is a three-note horn cell (D-F-E), the minor-second sigh in the violins and the dominant that never resolves.
| music_political-thriller_T03_sequel | sequel of T03 | 30 s | prompts/music_political-thriller_T03_sequel.txt | not rated | Seedance 2.5 video_extension forward of T03, 480p, 90 credits, job bedd31c8-7614-42aa-ac0f-ac9752ad8e60, Higgsfield MUSIC. Audio 32 kHz. |
| music_political-thriller_T03_full | complete 60 s, no picture range yet | 60 s | T03 + T03_sequel prompts | not rated | edit: T03 frames 0-719 + sequel end to end, no crossfade. Sequel starts at 30.00 s. Level -39 dB just before the join, -31 dB just after: an 8 dB step at 30 s. Sequel mean level stays -26 to -37 dB: it does not reach forte. |

## Composition plan: music_political-thriller_T03_sequel (Leonard 2026-11-23: a real 30 s sequel, Tom Clancy political thriller)

Seedance video_extension forward of T03, so the same orchestra and recording continue. D minor, 80 BPM, bars 11-20. Grows mezzo piano to forte; adds trumpets, trombones, timpani, military snare.

| Bars | Time after T03 | Notes and instruments | Harmony |
|---|---|---|---|
| 11-12 | 0-6 s | T03's held A resolves: low strings on D, soft timpani roll on D, snare enters quietly with a march pattern | D minor (the arrival T03 withheld) |
| 13-14 | 6-12 s | Cellos and basses: eighth-note ostinato on D, F, E; horns repeat T03's figure D-F-E, firm | D minor |
| 15-16 | 12-18 s | Trumpets and trombones: D-F-E then hold A, broad; snare stronger | D minor to B-flat |
| 17-18 | 18-24 s | Violins take the figure an octave up; timpani on every downbeat | B-flat, C, A major |
| 19-20 | 24-30 s | Full orchestra forte: horns and trumpets D-F-E, long A over snare roll and ostinato | A, unresolved |

## Reference analysis: "7 Minutes" (Seatbelts, Knockin' on Heaven's Door OST), Leonard's upload 2026-11-23

Measured with librosa and ffmpeg (file kept out of git: commercial recording). Measurements, not listening. Key estimates are weak (correlation 0.56).

- Length 6:46 (406 s). Tempo: tempogram peaks 74 to 76 BPM with a strong double-time 152 layer; 99 BPM is a weaker alternative.
- Harmony: no stable key. Centers move C#/F# (0:00-0:40), G and B minor (1:00-2:20), C# (2:40-4:40), A minor / B-flat (5:20-6:40). The strongest pitch pairs are half steps (A-B-flat, G-A-flat, C#-D): chromatic half-step tension.
- Arc (mean level, percussive share):
  - 0:00-0:40 quiet, low, -28 dB; percussive bursts at 0:20.
  - 0:40-1:20 first loud section, -14 dB, bright.
  - 1:20 drops to -23 dB, almost no percussion, low and heavy.
  - 1:40-2:40 back up to -13 dB with drums.
  - 3:00-4:40 long dark low section, high band under 3 %, low band up to 69 %.
  - 5:00-6:20 the loudest stretch, -11 dB, brightest.
  - 6:40 ends on percussive hits (91 % percussive).
- Instruments: not measurable from these numbers. Fan wiki credits synthesizer, string section and chorus (not verified).

### Full-track analysis (2 s chord windows, bass and top pitch, automatic segmentation). Automated estimates, noisy.

| Section | Time | Level | Harmony and bass | Character |
|---|---|---|---|---|
| A | 0:00-0:43 | -21 to -32 dB | F# major area, bass moves A#, F#, C#, D | quiet intro |
| B | 0:43-1:06 | -12 dB | E-flat minor, bass pedal F# and G (half step against each other), top note C#5 repeated | first loud block |
| C | 1:06-1:19 | -17 to -20 dB | G / G minor, A-flat | transition |
| D | 1:19-1:52 | -20 to -26 dB | B minor over a constant B1 pedal | held, darker |
| B2 | 1:52-2:27 | -12 dB | E-flat minor block returns, same F#/G bass, same repeated C#5 | return of B |
| E | 2:27-2:50 | -11 dB | F / F minor over bass A and G# alternating (half step) | first climax |
| F | 2:50-3:22 | -26 to -36 dB | C# minor pedal, near silence about 3:12 | drop |
| G | 3:22-4:46 | -26 rising to -15 dB | repeating 4-chord loop about every 10 s: B-flat minor, F#, G, C# (G is a tritone from C#), bass A#, A#, G, C# | long build on a loop |
| H | 4:46-5:15 | -24 to -40 dB | C#, near silence at 5:12 | breath before the peak |
| I | 5:15-5:50 | -11 dB | F / F minor / A minor over bass A and G# (half step) | main climax |
| J-K | 5:50-6:34 | -15 to -11 dB | A minor, then G minor / B-flat over a B-flat pedal | sustained loud ending |
| L | 6:34-6:46 | -22 dB | A minor, last low E hit | outro |

What drives it: pedal basses, half-step clashes (F# vs G, A vs G#), a repeated high C#, and in section G a 4-chord loop with a tritone (G inside C#) that repeats while the level rises 11 dB.

### First part in detail (0:00-2:50): pitch tracking on the harmonic layer, bass tracking, percussive onsets per 10 s

- A middle G (G3) sounds almost all the time under everything: a drone. Against the C# centres of the track it is a tritone.
- Percussion: 0:10-0:35 and 1:20-1:35 very dense, about 11 onsets a second (sixteenths at about 152 BPM); in the loud blocks 0:40-1:10 and 1:50-2:50 sparser, one every 0.2 to 0.4 s.
- Bass never sits still in the first minute: A1, D2, G#2 to G2, F#2, F3, G2 to F#1. Half steps down. Then a long B1 pedal 1:20-1:50.
- Top line is fragments, never a repeated tune: C#4 and E4 (0:10), D#5 jumping an octave to D#6 then A#5 (0:30), a held B5 (1:15), C#6 to F#5 (1:30).

## Method that follows the notes (2026-11-23)

Text prompts with exact notes are not followed (music_hybrid-thriller_T02: chroma correlation -0.01 with the score). Writing the score as MIDI (input/*_score.py), rendering it with FluidSynth and the FluidR3 General MIDI soundfont, and giving the render to Seedance 2.5 omni_reference as @audio1 does make it follow (T03: chroma 0.87, bass line matches bar by bar).

