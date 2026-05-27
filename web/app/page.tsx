import { SampleCard } from '@/components/SampleCard'
import styles from './page.module.css'

export default function Home() {
  return (
    <main className={styles.main}>
      <h1 className={styles.heading}>Of cards, quietly held</h1>
      <p className={styles.subhead}>
        A sample card composed entirely from theme tokens. In production this
        would be a real Scryfall image, framed by the same chrome.
      </p>
      <div className={styles.row}>
        <SampleCard />
      </div>
    </main>
  )
}
