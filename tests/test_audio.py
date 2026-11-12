"""The soundtrack: every track ships, moods switch without crashing."""

import unittest

from game import audio


class TestAudio(unittest.TestCase):

    def test_every_track_file_exists(self):
        for _name, filename in audio.TRACKS:
            with self.subTest(track=_name):
                self.assertIsNotNone(audio._track_file(_name),
                                     "%s is missing" % filename)

    def test_scene_mapping_covers_scenes(self):
        for scene in ("cover", "splash", "overworld", "finale",
                      "washup", "hub", "epilogue"):
            track = audio.SCENE_TRACK.get(scene, "dreamy")
            self.assertIsNotNone(audio._track_file(track))

    def test_mood_switching(self):
        audio.init()
        audio.play_music("overworld")
        self.assertEqual(audio._wanted_track(), "island")
        audio.set_mood("festival")
        self.assertEqual(audio._wanted_track(), "festival")
        audio.set_mood("nope")               # unknown moods clear, not crash
        self.assertIsNone(audio._mood)
        audio.play_music("cover")            # switches clear the mood
        self.assertIsNone(audio._mood)
        self.assertEqual(audio._wanted_track(), "garden")

    def test_music_mood_keys(self):
        self.assertEqual(len(audio.TRACKS), 7)


if __name__ == "__main__":
    unittest.main()
