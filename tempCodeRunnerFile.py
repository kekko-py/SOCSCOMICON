
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

        logging.debug("[QUEUES] Connessione chiusa e lock rilasciato")


# Chiama la funzione per inizializzare il database
init_sqlite()