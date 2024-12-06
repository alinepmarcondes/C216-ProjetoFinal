DROP TABLE IF EXISTS "vendas";
DROP TABLE IF EXISTS "produtos";

CREATE TABLE "produtos" (
    "id" SERIAL PRIMARY KEY,
    "nome" VARCHAR(255) NOT NULL,
    "marca" VARCHAR(255) NOT NULL,
    "animal" VARCHAR(255) NOT NULL,
    "idade" VARCHAR(255) NOT NULL,
    "quantidade" INTEGER NOT NULL,
    "preco" FLOAT NOT NULL
);

CREATE TABLE "vendas" (
    "id" SERIAL PRIMARY KEY,
    "produto_id" INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
    "quantidade_vendida" INTEGER NOT NULL,
    "valor_venda" FLOAT NOT NULL,
    "data_venda" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Ração', 'Purina', 'Cachorro', '1-2 anos', 50, 100.00);
INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Brinquedo de Borracha', 'Kong', 'Cachorro', '3-5 anos', 30, 25.00);
INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Ração Premium', 'Whiskas', 'Gato', '1-2 anos', 40, 120.00);
INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Areia Sanitária', 'Pipicat', 'Gato', 'Adulto', 60, 35.00);
INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Coleira com Guia', 'Ferplast', 'Cachorro', '6 meses - 1 ano', 20, 45.00);
INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Shampoo Neutro', 'Pet Society', 'Cachorro', 'Filhote', 25, 30.00);
INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Ração Especial', 'Alcon', 'Pássaro', 'Adulto', 15, 50.00);
INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Petisco Natural', 'Pedigree', 'Cachorro', '2-3 anos', 50, 20.00);
INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Cama Confortável', 'Truqys', 'Gato', 'Adulto', 10, 150.00);
INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Brinquedo de Pelúcia', 'Chalesco', 'Cachorro', 'Filhote', 35, 40.00);
INSERT INTO "produtos" ("nome", "marca", "animal", "idade", "quantidade", "preco") VALUES ('Comedouro de Inox', 'PetFlex', 'Gato', 'Todos', 20, 25.00);