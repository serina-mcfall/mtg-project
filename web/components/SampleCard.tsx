import styles from './SampleCard.module.css'

export function SampleCard() {
  return (
    <article className={styles.card} aria-label="Card: Sylvan Echo">
      <div className={styles.header}>
        <h3 className={styles.name}>Sylvan Echo</h3>
        <div className={styles.cost} aria-label="Mana cost: 2 generic, 1 green">
          <span className={`${styles.pip} ${styles.pipColourless}`} aria-hidden>
            2
          </span>
          <span className={styles.pip} aria-hidden>
            G
          </span>
        </div>
      </div>
      <div className={styles.art} role="img" aria-label="Card art placeholder" />
      <p className={styles.type}>Creature — Elf Druid</p>
      <p className={styles.text}>
        When Sylvan Echo enters the battlefield, search your library for a
        forest card and put it onto the battlefield tapped.
      </p>
      <p className={styles.flavour}>She listened, and the woods listened back.</p>
      <div className={styles.foot}>
        <span className={styles.set}>AVL · 142</span>
        <span className={styles.pt} aria-label="Power 2, toughness 3">
          2/3
        </span>
      </div>
    </article>
  )
}
