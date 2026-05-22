drop extension if exists "pg_net";

create sequence "public"."service_equipments_id_seq";

create sequence "public"."service_types_id_seq";


  create table "public"."branches" (
    "id" uuid not null default gen_random_uuid(),
    "name" text not null,
    "email" text not null,
    "latitude" double precision not null,
    "longitude" double precision not null,
    "created_at" timestamp with time zone default now()
      );


alter table "public"."branches" enable row level security;


  create table "public"."emergencies" (
    "id" uuid not null default gen_random_uuid(),
    "visit_id" text,
    "staff_id" text not null,
    "type" text not null,
    "latitude" double precision not null,
    "longitude" double precision not null,
    "status" text default 'Unresolved'::text,
    "created_at" timestamp with time zone default now()
      );


alter table "public"."emergencies" enable row level security;


  create table "public"."employees" (
    "id" uuid not null default gen_random_uuid(),
    "employee_id" character varying(50) not null,
    "name" character varying(100) not null,
    "branch_location" character varying(100) not null,
    "latitude" numeric(10,8),
    "longitude" numeric(11,8),
    "created_at" timestamp with time zone default now()
      );


alter table "public"."employees" enable row level security;


  create table "public"."service_equipments" (
    "id" integer not null default nextval('public.service_equipments_id_seq'::regclass),
    "service_type_id" integer,
    "item_name" character varying(100) not null,
    "is_mandatory" boolean default true
      );


alter table "public"."service_equipments" enable row level security;


  create table "public"."service_types" (
    "id" integer not null default nextval('public.service_types_id_seq'::regclass),
    "service_name" character varying(100) not null,
    "sla_duration_minutes" integer not null,
    "base_price" numeric(15,2) not null,
    "created_at" timestamp without time zone default now()
      );


alter table "public"."service_types" enable row level security;


  create table "public"."staff_locations" (
    "visit_id" text not null,
    "staff_id" text not null,
    "role" text not null,
    "latitude" double precision not null,
    "longitude" double precision not null,
    "updated_at" timestamp with time zone default now()
      );


alter table "public"."staff_locations" enable row level security;


  create table "public"."system_configs" (
    "config_key" text not null,
    "config_value" jsonb not null,
    "updated_at" timestamp with time zone default now()
      );


alter table "public"."system_configs" enable row level security;


  create table "public"."transactions" (
    "id" text not null,
    "patient" text not null,
    "phone" text not null,
    "service" text not null,
    "staff_id" text default '-'::text,
    "time" text not null,
    "order_status" text default 'Scheduled'::text,
    "visit_status" text default 'Waiting Assignment'::text,
    "branch" text not null,
    "notes" text,
    "nurse_lat" double precision,
    "nurse_lon" double precision,
    "sla_total" text default 'Pending'::text,
    "timeline" jsonb,
    "created_at" timestamp with time zone default now()
      );


alter table "public"."transactions" enable row level security;

alter sequence "public"."service_equipments_id_seq" owned by "public"."service_equipments"."id";

alter sequence "public"."service_types_id_seq" owned by "public"."service_types"."id";

CREATE UNIQUE INDEX branches_pkey ON public.branches USING btree (id);

CREATE UNIQUE INDEX emergencies_pkey ON public.emergencies USING btree (id);

CREATE UNIQUE INDEX employees_employee_id_key ON public.employees USING btree (employee_id);

CREATE UNIQUE INDEX employees_pkey ON public.employees USING btree (id);

CREATE UNIQUE INDEX service_equipments_pkey ON public.service_equipments USING btree (id);

CREATE UNIQUE INDEX service_types_pkey ON public.service_types USING btree (id);

CREATE UNIQUE INDEX staff_locations_pkey ON public.staff_locations USING btree (visit_id);

CREATE UNIQUE INDEX system_configs_pkey ON public.system_configs USING btree (config_key);

CREATE UNIQUE INDEX transactions_pkey ON public.transactions USING btree (id);

alter table "public"."branches" add constraint "branches_pkey" PRIMARY KEY using index "branches_pkey";

alter table "public"."emergencies" add constraint "emergencies_pkey" PRIMARY KEY using index "emergencies_pkey";

alter table "public"."employees" add constraint "employees_pkey" PRIMARY KEY using index "employees_pkey";

alter table "public"."service_equipments" add constraint "service_equipments_pkey" PRIMARY KEY using index "service_equipments_pkey";

alter table "public"."service_types" add constraint "service_types_pkey" PRIMARY KEY using index "service_types_pkey";

alter table "public"."staff_locations" add constraint "staff_locations_pkey" PRIMARY KEY using index "staff_locations_pkey";

alter table "public"."system_configs" add constraint "system_configs_pkey" PRIMARY KEY using index "system_configs_pkey";

alter table "public"."transactions" add constraint "transactions_pkey" PRIMARY KEY using index "transactions_pkey";

alter table "public"."emergencies" add constraint "emergencies_visit_id_fkey" FOREIGN KEY (visit_id) REFERENCES public.transactions(id) ON DELETE CASCADE not valid;

alter table "public"."emergencies" validate constraint "emergencies_visit_id_fkey";

alter table "public"."employees" add constraint "employees_employee_id_key" UNIQUE using index "employees_employee_id_key";

alter table "public"."service_equipments" add constraint "service_equipments_service_type_id_fkey" FOREIGN KEY (service_type_id) REFERENCES public.service_types(id) ON DELETE CASCADE not valid;

alter table "public"."service_equipments" validate constraint "service_equipments_service_type_id_fkey";

alter table "public"."staff_locations" add constraint "staff_locations_visit_id_fkey" FOREIGN KEY (visit_id) REFERENCES public.transactions(id) ON DELETE CASCADE not valid;

alter table "public"."staff_locations" validate constraint "staff_locations_visit_id_fkey";

grant delete on table "public"."branches" to "anon";

grant insert on table "public"."branches" to "anon";

grant references on table "public"."branches" to "anon";

grant select on table "public"."branches" to "anon";

grant trigger on table "public"."branches" to "anon";

grant truncate on table "public"."branches" to "anon";

grant update on table "public"."branches" to "anon";

grant delete on table "public"."branches" to "authenticated";

grant insert on table "public"."branches" to "authenticated";

grant references on table "public"."branches" to "authenticated";

grant select on table "public"."branches" to "authenticated";

grant trigger on table "public"."branches" to "authenticated";

grant truncate on table "public"."branches" to "authenticated";

grant update on table "public"."branches" to "authenticated";

grant delete on table "public"."branches" to "service_role";

grant insert on table "public"."branches" to "service_role";

grant references on table "public"."branches" to "service_role";

grant select on table "public"."branches" to "service_role";

grant trigger on table "public"."branches" to "service_role";

grant truncate on table "public"."branches" to "service_role";

grant update on table "public"."branches" to "service_role";

grant delete on table "public"."emergencies" to "anon";

grant insert on table "public"."emergencies" to "anon";

grant references on table "public"."emergencies" to "anon";

grant select on table "public"."emergencies" to "anon";

grant trigger on table "public"."emergencies" to "anon";

grant truncate on table "public"."emergencies" to "anon";

grant update on table "public"."emergencies" to "anon";

grant delete on table "public"."emergencies" to "authenticated";

grant insert on table "public"."emergencies" to "authenticated";

grant references on table "public"."emergencies" to "authenticated";

grant select on table "public"."emergencies" to "authenticated";

grant trigger on table "public"."emergencies" to "authenticated";

grant truncate on table "public"."emergencies" to "authenticated";

grant update on table "public"."emergencies" to "authenticated";

grant delete on table "public"."emergencies" to "service_role";

grant insert on table "public"."emergencies" to "service_role";

grant references on table "public"."emergencies" to "service_role";

grant select on table "public"."emergencies" to "service_role";

grant trigger on table "public"."emergencies" to "service_role";

grant truncate on table "public"."emergencies" to "service_role";

grant update on table "public"."emergencies" to "service_role";

grant delete on table "public"."employees" to "anon";

grant insert on table "public"."employees" to "anon";

grant references on table "public"."employees" to "anon";

grant select on table "public"."employees" to "anon";

grant trigger on table "public"."employees" to "anon";

grant truncate on table "public"."employees" to "anon";

grant update on table "public"."employees" to "anon";

grant delete on table "public"."employees" to "authenticated";

grant insert on table "public"."employees" to "authenticated";

grant references on table "public"."employees" to "authenticated";

grant select on table "public"."employees" to "authenticated";

grant trigger on table "public"."employees" to "authenticated";

grant truncate on table "public"."employees" to "authenticated";

grant update on table "public"."employees" to "authenticated";

grant delete on table "public"."employees" to "service_role";

grant insert on table "public"."employees" to "service_role";

grant references on table "public"."employees" to "service_role";

grant select on table "public"."employees" to "service_role";

grant trigger on table "public"."employees" to "service_role";

grant truncate on table "public"."employees" to "service_role";

grant update on table "public"."employees" to "service_role";

grant delete on table "public"."service_equipments" to "anon";

grant insert on table "public"."service_equipments" to "anon";

grant references on table "public"."service_equipments" to "anon";

grant select on table "public"."service_equipments" to "anon";

grant trigger on table "public"."service_equipments" to "anon";

grant truncate on table "public"."service_equipments" to "anon";

grant update on table "public"."service_equipments" to "anon";

grant delete on table "public"."service_equipments" to "authenticated";

grant insert on table "public"."service_equipments" to "authenticated";

grant references on table "public"."service_equipments" to "authenticated";

grant select on table "public"."service_equipments" to "authenticated";

grant trigger on table "public"."service_equipments" to "authenticated";

grant truncate on table "public"."service_equipments" to "authenticated";

grant update on table "public"."service_equipments" to "authenticated";

grant delete on table "public"."service_equipments" to "service_role";

grant insert on table "public"."service_equipments" to "service_role";

grant references on table "public"."service_equipments" to "service_role";

grant select on table "public"."service_equipments" to "service_role";

grant trigger on table "public"."service_equipments" to "service_role";

grant truncate on table "public"."service_equipments" to "service_role";

grant update on table "public"."service_equipments" to "service_role";

grant delete on table "public"."service_types" to "anon";

grant insert on table "public"."service_types" to "anon";

grant references on table "public"."service_types" to "anon";

grant select on table "public"."service_types" to "anon";

grant trigger on table "public"."service_types" to "anon";

grant truncate on table "public"."service_types" to "anon";

grant update on table "public"."service_types" to "anon";

grant delete on table "public"."service_types" to "authenticated";

grant insert on table "public"."service_types" to "authenticated";

grant references on table "public"."service_types" to "authenticated";

grant select on table "public"."service_types" to "authenticated";

grant trigger on table "public"."service_types" to "authenticated";

grant truncate on table "public"."service_types" to "authenticated";

grant update on table "public"."service_types" to "authenticated";

grant delete on table "public"."service_types" to "service_role";

grant insert on table "public"."service_types" to "service_role";

grant references on table "public"."service_types" to "service_role";

grant select on table "public"."service_types" to "service_role";

grant trigger on table "public"."service_types" to "service_role";

grant truncate on table "public"."service_types" to "service_role";

grant update on table "public"."service_types" to "service_role";

grant delete on table "public"."staff_locations" to "anon";

grant insert on table "public"."staff_locations" to "anon";

grant references on table "public"."staff_locations" to "anon";

grant select on table "public"."staff_locations" to "anon";

grant trigger on table "public"."staff_locations" to "anon";

grant truncate on table "public"."staff_locations" to "anon";

grant update on table "public"."staff_locations" to "anon";

grant delete on table "public"."staff_locations" to "authenticated";

grant insert on table "public"."staff_locations" to "authenticated";

grant references on table "public"."staff_locations" to "authenticated";

grant select on table "public"."staff_locations" to "authenticated";

grant trigger on table "public"."staff_locations" to "authenticated";

grant truncate on table "public"."staff_locations" to "authenticated";

grant update on table "public"."staff_locations" to "authenticated";

grant delete on table "public"."staff_locations" to "service_role";

grant insert on table "public"."staff_locations" to "service_role";

grant references on table "public"."staff_locations" to "service_role";

grant select on table "public"."staff_locations" to "service_role";

grant trigger on table "public"."staff_locations" to "service_role";

grant truncate on table "public"."staff_locations" to "service_role";

grant update on table "public"."staff_locations" to "service_role";

grant delete on table "public"."system_configs" to "anon";

grant insert on table "public"."system_configs" to "anon";

grant references on table "public"."system_configs" to "anon";

grant select on table "public"."system_configs" to "anon";

grant trigger on table "public"."system_configs" to "anon";

grant truncate on table "public"."system_configs" to "anon";

grant update on table "public"."system_configs" to "anon";

grant delete on table "public"."system_configs" to "authenticated";

grant insert on table "public"."system_configs" to "authenticated";

grant references on table "public"."system_configs" to "authenticated";

grant select on table "public"."system_configs" to "authenticated";

grant trigger on table "public"."system_configs" to "authenticated";

grant truncate on table "public"."system_configs" to "authenticated";

grant update on table "public"."system_configs" to "authenticated";

grant delete on table "public"."system_configs" to "service_role";

grant insert on table "public"."system_configs" to "service_role";

grant references on table "public"."system_configs" to "service_role";

grant select on table "public"."system_configs" to "service_role";

grant trigger on table "public"."system_configs" to "service_role";

grant truncate on table "public"."system_configs" to "service_role";

grant update on table "public"."system_configs" to "service_role";

grant delete on table "public"."transactions" to "anon";

grant insert on table "public"."transactions" to "anon";

grant references on table "public"."transactions" to "anon";

grant select on table "public"."transactions" to "anon";

grant trigger on table "public"."transactions" to "anon";

grant truncate on table "public"."transactions" to "anon";

grant update on table "public"."transactions" to "anon";

grant delete on table "public"."transactions" to "authenticated";

grant insert on table "public"."transactions" to "authenticated";

grant references on table "public"."transactions" to "authenticated";

grant select on table "public"."transactions" to "authenticated";

grant trigger on table "public"."transactions" to "authenticated";

grant truncate on table "public"."transactions" to "authenticated";

grant update on table "public"."transactions" to "authenticated";

grant delete on table "public"."transactions" to "service_role";

grant insert on table "public"."transactions" to "service_role";

grant references on table "public"."transactions" to "service_role";

grant select on table "public"."transactions" to "service_role";

grant trigger on table "public"."transactions" to "service_role";

grant truncate on table "public"."transactions" to "service_role";

grant update on table "public"."transactions" to "service_role";


