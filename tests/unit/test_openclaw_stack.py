import aws_cdk as cdk
from aws_cdk.assertions import Match, Template

from cdk.constants import REGION
from cdk.openclaw_stack import OpenClawStack


def _create_template() -> Template:
    app = cdk.App()
    stack = OpenClawStack(app, 'TestStack', env=cdk.Environment(account='123456789012', region=REGION))
    return Template.from_stack(stack)


class TestAiAgent:
    def test_instance_uses_openclaw_blueprint(self):
        template = _create_template()
        template.has_resource_properties(
            'AWS::Lightsail::Instance',
            {
                'BlueprintId': 'openclaw_ls_1_0',
                'InstanceName': 'openclaw-agent',
            },
        )

    def test_instance_uses_recommended_bundle(self):
        template = _create_template()
        template.has_resource_properties(
            'AWS::Lightsail::Instance',
            {
                'BundleId': 'medium_3_0',
            },
        )

    def test_instance_has_auto_snapshot(self):
        template = _create_template()
        template.has_resource_properties(
            'AWS::Lightsail::Instance',
            {
                'AddOns': [
                    Match.object_like(
                        {
                            'AddOnType': 'AutoSnapshot',
                        }
                    ),
                ],
            },
        )


class TestAiAgentNetworking:
    def test_static_ip_exists(self):
        template = _create_template()
        template.has_resource_properties(
            'AWS::Lightsail::StaticIp',
            {
                'StaticIpName': 'openclaw-agent-ip',
                'AttachedTo': 'openclaw-agent',
            },
        )

    def test_resource_count(self):
        template = _create_template()
        template.resource_count_is('AWS::Lightsail::Instance', 1)
        template.resource_count_is('AWS::Lightsail::StaticIp', 1)


class TestSecurity:
    def test_instance_has_firewall_rules(self):
        template = _create_template()
        template.has_resource_properties(
            'AWS::Lightsail::Instance',
            {
                'Networking': Match.object_like(
                    {
                        'Ports': Match.array_with(
                            [
                                Match.object_like({'FromPort': 443, 'ToPort': 443, 'Protocol': 'tcp'}),
                            ]
                        ),
                    }
                ),
            },
        )

    def test_firewall_includes_https(self):
        template = _create_template()
        template.has_resource_properties(
            'AWS::Lightsail::Instance',
            {
                'Networking': Match.object_like(
                    {
                        'Ports': Match.array_with(
                            [
                                Match.object_like({'FromPort': 443, 'ToPort': 443}),
                            ]
                        ),
                    }
                ),
            },
        )

    def test_firewall_includes_ssh(self):
        template = _create_template()
        template.has_resource_properties(
            'AWS::Lightsail::Instance',
            {
                'Networking': Match.object_like(
                    {
                        'Ports': Match.array_with(
                            [
                                Match.object_like({'FromPort': 22, 'ToPort': 22}),
                            ]
                        ),
                    }
                ),
            },
        )

    def test_no_unexpected_resource_types(self):
        """Ensure only expected resource types are created."""
        template = _create_template()
        template.resource_count_is('AWS::Lightsail::Instance', 1)
        template.resource_count_is('AWS::Lightsail::StaticIp', 1)
        # Verify no other resource types snuck in
        resources = template.to_json().get('Resources', {})
        resource_types = {r['Type'] for r in resources.values()}
        assert resource_types == {'AWS::Lightsail::Instance', 'AWS::Lightsail::StaticIp'}

    def test_tags_are_applied(self):
        app = cdk.App()
        stack = OpenClawStack(app, 'TagTestStack', env=cdk.Environment(account='123456789012', region=REGION))
        cdk.Tags.of(app).add('Project', 'OpenClaw')
        template = Template.from_stack(stack)
        template.has_resource_properties(
            'AWS::Lightsail::Instance',
            {
                'Tags': Match.array_with(
                    [
                        Match.object_like({'Key': 'Project', 'Value': 'OpenClaw'}),
                    ]
                ),
            },
        )
