import Layout from '../../components/Layout';
import BatchForm from '../../components/BatchForm';

export default function BatchPage() {
  return (
    <Layout>
      <section className="section">
        <div className="container">
          <h1 style={{ marginTop: 0 }}>Batch classification</h1>
          <p className="lead">Drop in structured JSON to triage newsletters and campaign bursts quickly.</p>
          <BatchForm />
        </div>
      </section>
    </Layout>
  );
}
