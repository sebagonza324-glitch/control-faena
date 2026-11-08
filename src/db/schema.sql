CREATE TABLE trabajador (
    id_trabajador INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(12) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    cargo VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE inicio_turno (
    id_turno INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(12) NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    CONSTRAINT fk_inicio_turno_trabajador
        FOREIGN KEY (rut) REFERENCES trabajador (rut)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE salida_turno (
    id_salida INT AUTO_INCREMENT PRIMARY KEY,
    id_turno INT NOT NULL UNIQUE,
    fecha_salida DATETIME NOT NULL,
    CONSTRAINT fk_salida_turno_inicio
        FOREIGN KEY (id_turno) REFERENCES inicio_turno (id_turno)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
