# class TestReflection(TestCase):
#     def setUp(self):
#         ioc.register_value('event_key', 'event')

#     @case(lambda: raise_(ValueError))
#     @case(lambda event: raise_(ValueError))
#     def test_get_event_handler(self, command):
#         handler = tested.get_event_handler(command)
#         with self.assertRaises(ValueError):
#             handler(object())

#     def test_get_event_handler_event(self):
#         expected = object()
#         handler = tested.get_event_handler(lambda event, ex=expected: self.assertEqual(event, ex))
#         handler(expected)

# def raise_(ex):
#     raise ex
