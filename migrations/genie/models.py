from django.db import models
from psqlextra.models import PostgresModel
from django.contrib.postgres.fields import ArrayField
from datetime import datetime


class GenieCompanies(PostgresModel):
    name = models.CharField(max_length=256, null=True, blank=True)
    website = models.URLField(unique=True)
    datetime = models.DateTimeField()

    class Meta:
        db_table = "genie_companies"
        get_latest_by = ["datetime"]
        ordering = ["-website", "-datetime"]
        indexes = [
            models.Index(fields=["website"]),
        ]


class GenieUsers(PostgresModel):
    username = models.CharField(max_length=256, null=True, blank=True, unique=True)
    password = models.CharField(max_length=64, null=True, blank=True)
    datetime = models.DateTimeField()
    database_url = models.CharField(max_length=2048, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=64, null=True, blank=True)
    team_id_slack = models.CharField(max_length=32, null=True, blank=True)
    user_id_slack = models.CharField(max_length=32, null=True, blank=True)
    role = models.CharField(max_length=16, null=True, blank=True)
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )

    class Meta:
        db_table = "genie_users"
        get_latest_by = ["datetime"]
        ordering = ["-username", "-datetime"]
        indexes = [
            models.Index(fields=["username"]),
        ]


class GenieUsersDatabaseConnection(PostgresModel):
    name = models.CharField(max_length=128, null=True, blank=True)
    host = models.CharField(max_length=512, null=True, blank=True)
    port = models.CharField(max_length=64, null=True, blank=True)
    ssl = models.BooleanField(null=True, blank=True)
    databasename = models.CharField(max_length=512, null=True, blank=True)
    username = models.CharField(max_length=512, null=True, blank=True)
    password = models.CharField(max_length=512, null=True, blank=True)
    apikey = models.CharField(max_length=512, null=True, blank=True)
    resourcename = models.CharField(max_length=512, null=True, blank=True)
    genie_users_id = models.ForeignKey(GenieUsers, on_delete=models.CASCADE, db_column='genie_users_id',
                                       related_name='db_connections')
    datetime = models.DateTimeField()
    connection_string_url = models.CharField(max_length=2048, null=True, blank=True)
    db_type = models.CharField(max_length=64, null=True, blank=True)
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )

    is_sync = models.BooleanField(blank=True, default=False)
    last_sync = models.DateTimeField(blank=True, default=False)

    class Meta:
        db_table = "genie_users_database_connection"
        get_latest_by = ["datetime"]
        ordering = ["-genie_users_id", "-datetime"]
        indexes = [
            models.Index(fields=["genie_users_id"]),
        ]
        unique_together = ("genie_users_id", "name", "resourcename")


class GenieUsersDatabaseConnectionDetails(PostgresModel):
    table_name = models.CharField(max_length=255)
    db_schema = models.CharField(max_length=255, blank=True, default="")
    db_warehouse = models.CharField(max_length=255, blank=True, default="")
    resourcename = models.CharField(max_length=512, null=True, blank=True)

    # The structure of the JSON objects is validated in application logic
    table_columns = models.JSONField(default=list)  # {"name": "column_name","type": "column_type"}
    foreign_keys = models.JSONField(
        default=list)  # {"name": "","constrained_columns": [""],"referred_schema":"","referred_table":"","referred_columns":[""],"options":[""]}

    examples = models.JSONField(default=list)  # Django's JSONField to store list of examples
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )
    status = models.CharField(
        max_length=15,
        choices=[
            ('COMPLETED', 'COMPLETED'),
            ('FAILED', 'FAILED')
        ],
        default='COMPLETED'
    )
    datetime = models.DateTimeField(default=datetime.now)
    genie_users = models.ForeignKey(GenieUsers, on_delete=models.CASCADE, db_column='genie_users_id')
    description = models.CharField(max_length=8192, null=True, blank=True)
    table_schema = models.CharField(max_length=16384, null=True, blank=True)

    class Meta:
        db_table = 'genie_users_db_connection_details'
        indexes = [
            models.Index(fields=["company_id", "table_name", "db_schema", "db_warehouse", "resourcename"]),
            models.Index(fields=["company_id", "table_name", "resourcename"]),
        ]
        unique_together = ("company_id", "table_name", "db_schema", "db_warehouse", "resourcename")
        ordering = ["-datetime"]


class GenieUsersDatabaseConnectionDetailsDescription(PostgresModel):
    table_name = models.CharField(max_length=255)
    db_schema = models.CharField(max_length=255, blank=True, default="")
    db_warehouse = models.CharField(max_length=255, blank=True, default="")
    resourcename = models.CharField(max_length=512, blank=True, default="")
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )

    datetime = models.DateTimeField(default=datetime.now)

    column_name = models.CharField(max_length=512, null=True, blank=True)
    column_description = models.CharField(max_length=8192, null=True, blank=True)

    column_distinct = models.JSONField(default=list)


    class Meta:
        db_table = 'genie_users_db_connection_details_column_description'
        indexes = [
            models.Index(
                fields=["company_id", "table_name", "db_schema", "db_warehouse", "resourcename", "column_name"]),
            models.Index(fields=["company_id", "table_name", "db_schema", "db_warehouse", "resourcename"]),
            models.Index(fields=["company_id", "table_name", "resourcename"]),
        ]
        unique_together = ("table_name", "db_schema", "db_warehouse", "resourcename", "company_id", "column_name")
        ordering = ["-datetime"]


class GenieUsersDatabaseGuardrails(PostgresModel):
    table_name = models.CharField(max_length=255, null=True, blank=True)
    db_schema = models.CharField(max_length=255, blank=True, default="")
    resourcename = models.CharField(max_length=512, null=True, blank=True)
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )
    genie_users = models.ForeignKey(GenieUsers, on_delete=models.CASCADE, db_column='genie_users_id')
    table_column = models.CharField(max_length=512, null=True, blank=True)
    access_type = models.IntegerField(default=0)  # 1=none, 0=read, 2=write
    datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    db_warehouse = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = 'genie_users_db_guardrails'


class GeniePaymentPlan(PostgresModel):
    plan = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=512, null=True, blank=True)
    amount = models.FloatField()
    stripe_price_id = models.CharField(max_length=40, null=True, blank=True)
    datetime = models.DateTimeField()

    class Meta:
        db_table = "genie_payment_plan"
        get_latest_by = ["datetime"]
        ordering = ["-amount"]
        indexes = [
            models.Index(fields=["plan"]),
        ]


class GenieChatHistory(PostgresModel):
    genie_users_id = models.ForeignKey(GenieUsers, on_delete=models.CASCADE, db_column='genie_users_id')
    datetime = models.DateTimeField()
    question = models.CharField(max_length=8192, null=True, blank=True)
    question_hash = models.CharField(max_length=64, null=True, blank=True)
    answer = models.CharField(max_length=8192, null=True, blank=True)
    team_id_slack = models.CharField(max_length=32, null=True, blank=True)
    user_id_slack = models.CharField(max_length=32, null=True, blank=True)
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )
    is_answered = models.BooleanField()
    db_schema = models.CharField(max_length=255, blank=True, default="")
    db_warehouse = models.CharField(max_length=255, blank=True, default="")
    table_name = models.CharField(max_length=255, null=True, blank=True)
    resourcename = models.CharField(max_length=512, null=True, blank=True)
    ai_engine = models.CharField(max_length=32, null=True, blank=True)
    ai_temp = models.FloatField(default=0, null=True, blank=True)  # 0.0
    ai_model = models.CharField(max_length=255, null=True, blank=True)  # GPT-3.5
    results_len = models.IntegerField(default=0)
    score = models.FloatField(default=0)
    ai_response = models.CharField(max_length=8192, null=True, blank=True)
    intermediate_steps = models.JSONField(default=list, null=True, blank=True)
    chart_code = models.CharField(max_length=16384, null=True, blank=True)
    chart_image_url = models.URLField(null=True, blank=True)
    total_tokens = models.IntegerField(default=0, null=True, blank=True)
    total_cost = models.FloatField(default=0, null=True, blank=True)
    total_time = models.FloatField(default=0, null=True, blank=True)
    status = models.IntegerField(default=0, null=True,
                                 blank=True)  # 0=waiting, 1=processing_sql, 2=completed_sql, 3=error
    error_msg = models.CharField(max_length=8192, null=True, blank=True)
    client_type = models.FloatField(default=0, null=True, blank=True)  # 0=slack, 1=app,
    results_s3_key = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "genie_chat_history"
        get_latest_by = ["datetime"]
        ordering = ["-datetime"]
        indexes = [
            models.Index(fields=["datetime"]),
            models.Index(fields=["genie_users_id"]),
            models.Index(fields=["genie_users_id", "datetime"]),
            models.Index(fields=["genie_users_id", "user_id_slack", "datetime"]),
            models.Index(fields=["company_id", "resourcename", "user_id_slack", "team_id_slack", "genie_users_id"]),

        ]


class GenieApprovedQuestions(PostgresModel):
    question = models.CharField(max_length=8192, unique=True)
    answer = models.CharField(max_length=8192, null=True, blank=True)
    chart_code = models.CharField(max_length=16384, null=True, blank=True)
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )
    datetime = models.DateTimeField()
    approved_by = models.ForeignKey(GenieUsers, on_delete=models.CASCADE, db_column='approved_by')
    db_schema = models.CharField(max_length=255, blank=True, default="")
    db_warehouse = models.CharField(max_length=255, blank=True, default="")
    resourcename = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        db_table = "genie_approved_questions"
        get_latest_by = ["datetime"]
        ordering = ["-datetime"]
        indexes = [
            models.Index(fields=["datetime"]),
            models.Index(fields=["company_id", "datetime"]),
        ]


class GenieUsersPayments(PostgresModel):
    client_secret = models.CharField(max_length=128, null=True, blank=True)
    payment_intent = models.CharField(max_length=128, null=True, blank=True)
    subscription_id = models.CharField(max_length=128, null=True, blank=True)
    genie_users_id = models.ForeignKey(GenieUsers, on_delete=models.CASCADE, db_column='genie_users_id')
    genie_payment_plan_id = models.ForeignKey(GeniePaymentPlan, on_delete=models.CASCADE,
                                              db_column='genie_payment_plan_id')
    provider = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=16, null=True, blank=True)  # intent, trial, succeeded
    datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )
    subscription_start_date = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    subscription_status = models.CharField(max_length=32, null=True, blank=True)  # intent, trial, succeeded
    subscription_current_period_start_date = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    subscription_current_period_end_date = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    subscription_item_id = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        db_table = "genie_users_payments"
        get_latest_by = ["datetime"]
        ordering = ["-genie_users_id", "-datetime"]
        indexes = [
            models.Index(fields=["genie_users_id"]),
        ]
        unique_together = ("genie_users_id", "client_secret", "payment_intent")


class GenieAPIKeys(models.Model):
    key_hash = models.CharField(max_length=255, unique=True)
    key_unsafe = models.CharField(max_length=255, null=True, blank=True)
    usage_limit = models.IntegerField(default=0)
    usage_count = models.IntegerField(default=0)
    genie_users_id = models.ForeignKey(GenieUsers, on_delete=models.CASCADE, db_column='genie_users_id')
    allowed_paths = ArrayField(
        models.CharField(blank=True, max_length=256),
        default=list,
    )
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )

    class Meta:
        db_table = "genie_api_keys"
        indexes = [
            models.Index(fields=["key_hash"]),
            models.Index(fields=["genie_users_id"]),
        ]


class GenieUserInvitations(PostgresModel):
    email = models.CharField(max_length=256, null=True, blank=True)
    secret_code = models.CharField(max_length=32, unique=True)
    genie_users_id = models.ForeignKey(GenieUsers, on_delete=models.CASCADE, db_column='genie_users_id')
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )
    team_id_slack = models.CharField(max_length=32, null=True, blank=True)
    user_id_slack = models.CharField(max_length=32, null=True, blank=True)
    invite_type = models.CharField(max_length=32, null=True, blank=True)
    datetime = models.DateTimeField()

    class Meta:
        db_table = "genie_user_invitations"
        get_latest_by = ["datetime"]
        ordering = ["-email", "-datetime"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["secret_code"]),
        ]


class GenieUserLoginMagicLinks(PostgresModel):
    email = models.CharField(max_length=256, null=True, blank=True)
    secret_code = models.CharField(max_length=32, unique=True)
    genie_users_id = models.ForeignKey(GenieUsers, on_delete=models.CASCADE, db_column='genie_users_id')
    company_id = models.ForeignKey(GenieCompanies, on_delete=models.CASCADE, db_column='company_id', )
    datetime = models.DateTimeField()

    class Meta:
        db_table = "genie_user_login_magic_link"
        get_latest_by = ["datetime"]
        ordering = ["-email", "-datetime"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["secret_code"]),
        ]


