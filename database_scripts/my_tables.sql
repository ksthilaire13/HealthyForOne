create table users
(
    user_id      integer not null
        constraint user_pk
            primary key autoincrement,
    username     text    not null,
    email    text    not null,
    password text    not null,
    name text,
    bio text,
    photo text,
    date_registered text
);


create table run
(
    run_id   integer not null
        constraint run_pk
            primary key autoincrement,
    distance float    not null,
    duration    text    not null,
    effort       integer,
    temp integer,
    time_of_day     text not null,
    date text not null,
    weather text not null,
    notes text not null,
    user_id int not null
        constraint run_fk
            references users
);


create table venues
(
    sleep_id          integer not null
        constraint sleep_pk
            primary key autoincrement,
    date        text    not null,
    bedtime     text    not null,
    wake_up text not null,
    times_awoken      integer,
    dreams_torf text,
    sleep_notes text,
    user_id           integer not null
        constraint sleep_fk
            references users
);