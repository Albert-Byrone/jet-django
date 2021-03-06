from jet_django.admin.model_description import JetAdminModelDescription
from rest_framework import views
from rest_framework.response import Response
from django.apps import apps

from jet_django.permissions import HasProjectPermissions


class JetAdmin(object):
    models = []

    def models_view(self):
        Admin = self

        class View(views.APIView):
            authentication_classes = ()
            permission_classes = (HasProjectPermissions,)

            def get(self, request, *args, **kwargs):
                return Response(map(lambda x: x.serialize(), Admin.models))

        return View

    def register(self, Model, fields=None, actions=list(), ordering_field=None, hidden=False):
        self.models.append(JetAdminModelDescription(Model, fields, actions, ordering_field, hidden))

    def register_related_models(self):
        def model_key(x):
            return '{}_{}'.format(
                x['app_label'],
                x['model']
            )
        registered = set(map(lambda x: model_key(x.get_model()), self.models))

        for models_description in self.models:
            for item in models_description.get_related_models():
                key = model_key(item['model_info'])

                if key in registered:
                    continue

                self.register(item['model'], hidden=True)
                registered.add(key)

jet = JetAdmin()

models = apps.get_models()

for model in models:
    jet.register(model)
